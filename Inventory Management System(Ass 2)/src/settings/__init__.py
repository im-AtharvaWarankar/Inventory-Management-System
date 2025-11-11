from .base import *
ENV = os.getenv('ENV', None)

# if os.environ['ENV'] == 'prod':
if ENV == 'prod':
   from .prod import *
else:
   from .dev import *