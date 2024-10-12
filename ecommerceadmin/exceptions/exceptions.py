#CLASES Y FUNCIONES DE MANEJO DE EXCEPCIONES
from django.http import JsonResponse

class ExceptionBaseError(Exception):
    pass

#LADO DE USUARIO
#Register users
class RegisterUser(ExceptionBaseError):
    def __init__(self, message="Error al registrar usuario"):
        self.message = message
        super().__init__(self.message)
        
class UserNotFound(RegisterUser):
    def __init__(self, user):
        self.user = f"Usuario {user} no registrado"
        super().__init__(self.user)
        
class UserAlreadyExist(RegisterUser):
    def __init__(self, user):
        self.user = f"El usuario {user} ya ha sido registrado"
        super().__init__(self.user)

#Login Users
class LoginUser(ExceptionBaseError):
    def __init__(self, message="Usuario no registrado"):
        self.message = message
        super().__init__(self.message)
        
class UserLoginCredentials(LoginUser):
    def __init__(self, message="Usuario sin credenciales"):
        super().__init__(message)
        
class UserPasswordCredentials(LoginUser):
    def __init__(self, message="El password no corresponde a sus credenciales"):
        super().__init__(message)
        
def jsonResponses(e):
    if isinstance(e, UserNotFound):
        return JsonResponse({"error": str(e)}, status=404)
    elif isinstance(e, UserAlreadyExist):
        return JsonResponse({"error": str(e)}, status=409)
    elif isinstance(e, UserLoginCredentials):
        return JsonResponse({"error": str(e)}, status=401)
    elif isinstance(e, UserPasswordCredentials):
        return JsonResponse({"error": str(e)}, status=401)
    return JsonResponse({"error": "Error en el servidor"}, status=500)