#!/usr/bin/env python3
"""
Script to fill in Spanish translations for the Django blog application
"""

# Common Spanish translations dictionary
SPANISH_TRANSLATIONS = {
    # Comments and moderation
    "Rejected": "Rechazado",
    "Status": "Estado", 
    "Actions": "Acciones",
    "Approve": "Aprobar",
    "Reject": "Rechazar",
    "View Comment": "Ver comentario",
    "No comments pending moderation": "No hay comentarios pendientes de moderación",
    "No approved comments yet": "Aún no hay comentarios aprobados",
    "No rejected comments": "No hay comentarios rechazados",
    
    # Home page and articles
    "Latest Articles": "Últimos artículos",
    "Welcome to our Blog": "Bienvenido a nuestro blog",
    "Discover our latest articles and insights": "Descubra nuestros últimos artículos e ideas",
    "No articles available": "No hay artículos disponibles",
    "No articles match your search criteria": "Ningún artículo coincide con sus criterios de búsqueda",
    "Filter Articles": "Filtrar artículos",
    "Sort by": "Ordenar por",
    "Search": "Buscar",
    "Clear Filters": "Limpiar filtros",
    "Results found": "Resultados encontrados",
    
    # Authentication
    "Login to your account": "Inicie sesión en su cuenta",
    "Create a new account": "Crear una nueva cuenta",
    "Sign in": "Iniciar sesión",
    "Sign up": "Registrarse",
    "Remember me": "Recordarme",
    "Forgot your password?": "¿Olvidó su contraseña?",
    "Already have an account?": "¿Ya tiene una cuenta?",
    "Don't have an account?": "¿No tiene una cuenta?",
    "Account Registration": "Registro de cuenta",
    
    # User profile and settings
    "User Profile": "Perfil de usuario",
    "Profile Settings": "Configuración de perfil",
    "Change Password": "Cambiar contraseña",
    "Update Profile": "Actualizar perfil",
    "Account Settings": "Configuración de cuenta",
    
    # Search results
    "Search Results": "Resultados de búsqueda",
    "Search for:": "Buscar:",
    "Found": "Encontrado",
    "result": "resultado",
    "results": "resultados",
    "No results found": "No se encontraron resultados",
    "Try adjusting your search criteria": "Intente ajustar sus criterios de búsqueda",
    "Show more filters": "Mostrar más filtros",
    "Hide filters": "Ocultar filtros",
    "Reset search": "Restablecer búsqueda",
    
    # Date and time filters
    "just now": "ahora mismo",
    "1 minute ago": "hace 1 minuto",
    "{} minutes ago": "hace {} minutos",
    "1 hour ago": "hace 1 hora",
    "{} hours ago": "hace {} horas",
    "1 day ago": "hace 1 día",
    "{} days ago": "hace {} días",
    "1 week ago": "hace 1 semana",
    "{} weeks ago": "hace {} semanas",
    "1 month ago": "hace 1 mes",
    "{} months ago": "hace {} meses",
    "1 year ago": "hace 1 año",
    "{} years ago": "hace {} años",
    
    # Reading time
    "1 minute read": "1 minuto de lectura",
    "{} minutes read": "{} minutos de lectura",
    "1 hour read": "1 hora de lectura",
    "1 hour {} minutes read": "1 hora {} minutos de lectura",
    "{} hours read": "{} horas de lectura",
    "{} hours {} minutes read": "{} horas {} minutos de lectura",
    
    # General terms
    "Read more": "Leer más",
    "Show more": "Mostrar más",
    "Show less": "Mostrar menos",
    "Load more": "Cargar más",
    "Back": "Atrás",
    "Next": "Siguiente",
    "Previous": "Anterior",
    "Continue": "Continuar",
    "Submit": "Enviar",
    "Close": "Cerrar",
    "Open": "Abrir",
    "Settings": "Configuración",
    "Help": "Ayuda",
    "About": "Acerca de",
    "Contact": "Contacto",
    "Privacy": "Privacidad",
    "Terms": "Términos",
    "FAQ": "Preguntas frecuentes",
    "Support": "Soporte",
    "Feedback": "Comentarios",
    "Share": "Compartir",
    "Print": "Imprimir",
    "Download": "Descargar",
    "Upload": "Subir",
    "Export": "Exportar",
    "Import": "Importar",
    "Copy": "Copiar",
    "Paste": "Pegar",
    "Cut": "Cortar",
    "Undo": "Deshacer",
    "Redo": "Rehacer",
    "Refresh": "Actualizar",
    "Reload": "Recargar",
    "Loading...": "Cargando...",
    "Please wait...": "Por favor espere...",
    "Error": "Error",
    "Warning": "Advertencia",
    "Success": "Éxito",
    "Information": "Información",
    "Yes": "Sí",
    "No": "No",
    "OK": "Aceptar",
    "Cancel": "Cancelar",
    "Apply": "Aplicar",
    "Reset": "Restablecer",
    "Clear": "Limpiar",
    "All": "Todos",
    "None": "Ninguno",
    "Select": "Seleccionar",
    "Unselect": "Deseleccionar",
    "Select all": "Seleccionar todo",
    "Unselect all": "Deseleccionar todo",
    "Toggle": "Alternar",
    "Enable": "Habilitar",
    "Disable": "Deshabilitar",
    "Show": "Mostrar",
    "Hide": "Ocultar",
    "Expand": "Expandir",
    "Collapse": "Contraer",
    "Minimize": "Minimizar",
    "Maximize": "Maximizar",
    "Full screen": "Pantalla completa",
    "Exit full screen": "Salir de pantalla completa",
    "Zoom in": "Acercar",
    "Zoom out": "Alejar",
    "Fit to window": "Ajustar a ventana",
    "Actual size": "Tamaño real",
}

def main():
    print("Spanish translation dictionary created with {} translations".format(len(SPANISH_TRANSLATIONS)))
    print("Use this dictionary to manually fill in the remaining translations.")
    
    # Print some examples
    print("\nSome example translations:")
    for i, (en, es) in enumerate(list(SPANISH_TRANSLATIONS.items())[:10]):
        print(f"  {en} -> {es}")
    
    print(f"\n... and {len(SPANISH_TRANSLATIONS) - 10} more translations available.")

if __name__ == "__main__":
    main()
