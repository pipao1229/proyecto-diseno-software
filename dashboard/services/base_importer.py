# dashboard/services/base_importer.py

from abc import ABC, abstractmethod

class BaseDataImporter(ABC):
    """
    Clase base abstracta (interfaz) para los importadores de datos.
    Este es el "Product" en el patrón Factory Method.
    """

    def __init__(self, file):
        if not hasattr(file, 'read'):
            raise TypeError("El objeto proporcionado debe ser un archivo.")
        self.file = file
        self.errors = []
        self.valid_records = []

    @abstractmethod
    def process_file(self):
        """
        Método principal que orquesta la lectura, validación y
        procesamiento del archivo. Debe ser implementado por subclases.
        """
        pass
    
    def get_results(self):
        """Devuelve los registros válidos y los errores encontrados."""
        return self.valid_records, self.errors