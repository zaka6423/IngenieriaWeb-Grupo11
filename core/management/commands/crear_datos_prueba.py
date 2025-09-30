from django.core.management.base import BaseCommand
from core.models import TipoPublicacion, TipoDonacion, Comedor, UserProfile, User, Publicacion, PublicacionArticulo
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Crea datos de prueba para la aplicación'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')
        
        # Crear tipos de publicación
        tipos_publicacion = [
            "Solicitud de alimentos",
            "Evento comunitario", 
            "Voluntariado",
            "Donación específica",
            "Urgente - Necesidad inmediata",
            "Campaña especial"
        ]
        
        for descripcion in tipos_publicacion:
            tipo, created = TipoPublicacion.objects.get_or_create(descripcion=descripcion)
            if created:
                self.stdout.write(f'✓ Creado tipo de publicación: {descripcion}')
        
        # Crear tipos de donación
        tipos_donacion = [
            "Alimentos no perecederos",
            "Productos frescos",
            "Ropa y abrigo",
            "Juguetes y libros",
            "Productos de higiene",
            "Dinero en efectivo",
            "Materiales de construcción",
            "Equipamiento de cocina"
        ]
        
        for descripcion in tipos_donacion:
            tipo, created = TipoDonacion.objects.get_or_create(descripcion=descripcion)
            if created:
                self.stdout.write(f'✓ Creado tipo de donación: {descripcion}')
        
        # Crear comedores de prueba si no existen
        comedores_data = [
            {
                'nombre': 'Comedor San Martín',
                'descripcion': 'Comedor comunitario que atiende a familias del barrio San Martín. Ofrecemos almuerzo y merienda de lunes a viernes.',
                'barrio': 'San Martín',
                'tipo': 'Comunitario',
                'capacidad': 80
            },
            {
                'nombre': 'Parroquia Nuestra Señora del Carmen',
                'descripcion': 'Comedor parroquial que brinda asistencia alimentaria a la comunidad. También organizamos actividades recreativas.',
                'barrio': 'Centro',
                'tipo': 'Parroquial',
                'capacidad': 120
            },
            {
                'nombre': 'Comedor Los Pibes',
                'descripcion': 'Comedor barrial gestionado por vecinos. Atendemos especialmente a niños y adolescentes en situación vulnerable.',
                'barrio': 'Villa Esperanza',
                'tipo': 'Barrial',
                'capacidad': 60
            },
            {
                'nombre': 'Centro Comunitario Solidario',
                'descripcion': 'Centro integral que incluye comedor, biblioteca y talleres. Trabajamos con voluntarios de la comunidad.',
                'barrio': 'Norte',
                'tipo': 'Centro Comunitario',
                'capacidad': 100
            }
        ]
        
        comedores_creados = []
        for data in comedores_data:
            comedor, created = Comedor.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            if created:
                comedores_creados.append(comedor)
                self.stdout.write(f'✓ Creado comedor: {data["nombre"]}')
        
        # Crear publicaciones de prueba si hay comedores
        if comedores_creados:
            tipos_pub = list(TipoPublicacion.objects.all())
            
            publicaciones_data = [
                {
                    'titulo': 'Necesitamos leche en polvo urgentemente',
                    'descripcion': 'Estamos con muy poca leche en polvo y necesitamos para los desayunos de esta semana. Cualquier cantidad es bienvenida.',
                    'tipo': 'Solicitud de alimentos'
                },
                {
                    'titulo': 'Evento solidario - Día del Niño',
                    'descripcion': 'Organizamos una fiesta para el Día del Niño. Necesitamos juguetes, golosinas y voluntarios para las actividades.',
                    'tipo': 'Evento comunitario'
                },
                {
                    'titulo': 'Buscamos voluntarios para cocina',
                    'descripcion': 'Necesitamos personas que puedan ayudar en la cocina los martes y jueves de 9 a 12 hs. No se requiere experiencia.',
                    'tipo': 'Voluntariado'
                },
                {
                    'titulo': 'Campaña de ropa de invierno',
                    'descripcion': 'Con el frío que se viene, estamos juntando abrigos, camperas y ropa de invierno para las familias del barrio.',
                    'tipo': 'Donación específica'
                }
            ]
            
            for i, data in enumerate(publicaciones_data):
                if i < len(comedores_creados):
                    comedor = comedores_creados[i]
                    tipo_pub = next((t for t in tipos_pub if t.descripcion == data['tipo']), tipos_pub[0])
                    
                    publicacion, created = Publicacion.objects.get_or_create(
                        titulo=data['titulo'],
                        comedor=comedor,
                        defaults={
                            'id_tipo_publicacion': tipo_pub,
                            'descripcion': data['descripcion'],
                            'fecha_inicio': timezone.now() - timedelta(days=random.randint(1, 7)),
                            'fecha_fin': timezone.now() + timedelta(days=random.randint(7, 30))
                        }
                    )
                    
                    if created:
                        # Agregar algunos artículos de ejemplo
                        articulos_ejemplo = [
                            'Leche en polvo 1kg',
                            'Azúcar 1kg', 
                            'Harina 000 1kg'
                        ] if 'leche' in data['titulo'].lower() else [
                            'Juguetes didácticos',
                            'Golosinas',
                            'Materiales para manualidades'
                        ]
                        
                        for articulo in articulos_ejemplo:
                            PublicacionArticulo.objects.create(
                                publicacion=publicacion,
                                nombre_articulo=articulo
                            )
                        
                        self.stdout.write(f'✓ Creada publicación: {data["titulo"]}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos de prueba creados exitosamente!')
        )
