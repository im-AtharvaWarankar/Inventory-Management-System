from rest_framework.viewsets import ModelViewSet
from rest_framework.views import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from users.models import Users
import django
from atomicloops.tasks import export_data


# Atomic View
class AtomicViewSet(ModelViewSet):
    # renderer_classes = AtomicJsonRenderer

    # # TODO  write queryset
    # def get_queryset(self):
    #     """
    #     1. filter inactive user
    #     2. filter level zero user
    #     3. Comments
    #     """
    #     if self.request.user_level == 0:
    #         return self.serializer_class.Meta.model.objects.all()
    #     if self.request.user_level == 5:
    #         return self.serializer_class.Meta.model.objects.exclude(userId__user_level=0)
    #     return self.serializer_class.Meta.model.objects.exclude(userId__is_active=False).exclude(userId__user_level=0)
    def validate_data(self, data):
        serializer_class = self.serializer_class or self.get_serializer_class()
        if serializer_class.Meta.model == Users:
            for item in data:
                if "email" not in item:
                    raise serializers.ValidationError(f'This Email field not provided for: {item}')
                email_check = {"email": item["email"]}
                if serializer_class.Meta.model.objects.filter(**email_check).exists():
                    raise serializers.ValidationError(f'This data already exists: {item}')
        else:
            for item in data:
                if serializer_class.Meta.model.objects.filter(**item).exists():
                    raise serializers.ValidationError(f'This data already exists: {item}')

    def validate_ids(self, data, field="id", unique=True):
        # new_data = []
        serializer_class = self.serializer_class or self.get_serializer_class()
        for item in data:
            if "id" not in item:
                raise serializers.ValidationError(f'Id Not provided {item}')

            if not serializer_class.Meta.model.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(f'Id does not Exists {item}')
            else:
                serializer_class.Meta.model.objects.filter(id=item['id']).update(**item)
        return [x[field] for x in data]

    @action(detail=False, methods=['post'], url_path='multiple-update')
    def multiple_update(self, request, *args, **kwargs):
        try:
            serializer_class = self.serializer_class or self.get_serializer_class()
            if not request.user.is_superuser:
                return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)
            if not isinstance(request.data, list):
                raise ValidationError('Request body must be a list')
            if request.data == []:
                raise ValidationError('Empty data not permitted')
            if len(request.data) > 100:
                raise ValidationError('Number of list elements must not be greater than 100')
            ids = self.validate_ids(request.data)
            instances = serializer_class.Meta.model.objects.filter(id__in=ids)
            fields = [f.name for f in serializer_class.Meta.model._meta.concrete_fields]
            fields.remove('id')
            _ = serializer_class.Meta.model.objects.bulk_update(instances, fields)
            serializer = serializer_class(instances, many=True, partial=True, context={'request': self.request, 'view': self})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='multiple-create')
    def multiple_create(self, request, *args, **kwargs):
        serializer_class = self.serializer_class or self.get_serializer_class()
        if not request.user.is_superuser:
            return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)
        if not isinstance(request.data, list):
            raise ValidationError('Request body must be a list')
        if request.data == []:
            raise ValidationError('Empty data not permitted')
        if len(request.data) > 100:
            raise ValidationError('Number of list elements must not be greater than 100')
        # Check data
        self.validate_data(request.data)
        serializers = serializer_class(data=request.data, many=True, context={'request': self.request, 'view': self})
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    def multiple_delete(self, request, *args, **kwargs):
        serializer_class = self.serializer_class or self.get_serializer_class()
        if not request.user.is_superuser:
            return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)
        if not isinstance(request.data, list):
            raise ValidationError('Request body must be a list')
        if request.data == []:
            raise ValidationError('Empty data not permitted')
        if len(request.data) > 100:
            raise ValidationError('Number of list elements must not be greater than 100')
        ids = self.validate_ids(request.data)
        instances = serializer_class.Meta.model.objects.filter(id__in=ids)
        instances.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except django.db.models.deletion.ProtectedError as e:
            return Response(status=status.HTTP_423_LOCKED, data={'detail': str(e)})
        except django.db.models.deletion.RestrictedError as e:
            return Response(status=status.HTTP_423_LOCKED, data={'detail': str(e)})
        # self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    # IMPORT DATA API
    @action(detail=False, methods=['post'], url_path='import-data')
    def import_data(self, request, *args, **kwargs):
        # Get file
        file = request.FILES["file"] if "file" in request.FILES else None
        # Check if file is present
        if file is None:
            return Response(
                {"message": "File Not Provided"}, status.HTTP_400_BAD_REQUEST
            )

        # read lines from tsv files
        data = (line.decode('utf-8').strip().replace('\n', '').split('\\t') for line in file.readlines())
        headers = data.__next__()
        qs = []
        for row in data:
            _object_dict = {key: value for key, value in zip(headers, row)}
            qs.append(_object_dict)

        serializer_class = self.serializer_class or self.get_serializer_class()
        if not request.user.is_superuser:
            return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)
        # if not isinstance(qs, list):
        #     raise ValidationError('Request body must be a list')
        if qs == []:
            raise ValidationError('Empty data not permitted')
        if len(qs) > 100:
            raise ValidationError('Number of list elements must not be greater than 100')
        self.validate_data(qs)

        serializers = serializer_class(data=qs, many=True, context={'request': self.request, 'view': self})
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    # export data api
    @action(detail=False, methods=['post'], url_path='export-data')
    def export_data(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)

        serializer_class = self.serializer_class or self.get_serializer_class()
        model = serializer_class.Meta.model.__name__
        app_name = serializer_class.Meta.model._meta.app_label

        export_data.delay(model, app_name, userId=request.user.id)
        return Response('In process!', status=status.HTTP_200_OK)
