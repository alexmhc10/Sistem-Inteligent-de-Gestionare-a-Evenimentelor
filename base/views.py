from django.shortcuts import render
from django.http import HttpResponse
from .models import Location


# locations = [
#     {'id' : 1,
#      'name': 'Romanita',
#      'description': 'Situată în inima orașului, Sala Regală oferă un cadru elegant pentru evenimente de amploare. Cu o capacitate de până la 500 de persoane, această sală este dotată cu tehnologie audio-vizuală de ultimă generație și un sistem de iluminat spectaculos. Decorul rafinat, cu candelabre strălucitoare și feronerie din aur, creează o atmosferă sofisticată, ideală pentru nunți, gale de premiere sau conferințe internaționale.',
#      'gallery': 'https://www.romanitahotel.ro/wp-content/uploads/2024/08/Sala-de-Evenimente-Romanita-Baia-Mare-3-min-1.png'
#      },

#      {
#          'id': 2,
#          'name': 'La Ionut',
#          'description': 'Grădina Verde este un spațiu idilic în aer liber, perfect pentru evenimente informale și petreceri de vară. Împădurită de copaci mari și flori colorate, această locație poate găzdui până la 300 de invitați. Facilitațile includ un podium pentru muzică live și o zonă de relaxare cu hamace, ideală pentru o atmosferă relaxantă și prietenoasă. Oferim opțiuni de catering cu preparate locale și organice.',
#          'gallery': 'https://www.weddingo.ro/_next/image?url=https%3A%2F%2Fhoneypot0.s3.amazonaws.com%2Fgallery%2F1716541034240-gallery-Sala%2520de%2520evenimente%2520La%2520Ionut%2520%2520%25281%2529.webp&w=1920&q=75'
#      },
#      {'id' :3,
#      'name': "Amour de l'evenement",
#      'description': 'Centrul de Conferințe Urban este o alegere excelentă pentru evenimente corporate și workshop-uri. Dotat cu săli multifuncționale, capacitatea totală variază între 50 și 400 de persoane, în funcție de aranjamentul dorit. Tehnologia de comunicație avansată și accesul la internet de mare viteză asigură un mediu de lucru eficient. Cafeneaua de pe loc oferă pauze de cafea și prânzuri sănătoase pentru participanți.',
#      'gallery': 'https://lh3.googleusercontent.com/p/AF1QipOVAmn9bMCrwcgDREO47-81ykn0vQdGVH42HYK1=s1360-w1360-h1020-rw'
#      },
#      {'id' : 4,
#      'name': 'Ghitta ',
#      'description': 'Teatrul Antic, cu o istorie bogată și o arhitectură impresionantă, este locul ideal pentru evenimente culturale, spectacole de teatru și concerte. Capacitatea sa de 600 de locuri oferă o experiență intimă, iar acustica excelentă garantează un sunet de calitate. Grădinile adiacente sunt perfecte pentru recepții și fotografii, creând un cadru de poveste pentru invitați.',
#      'gallery': 'https://lh3.googleusercontent.com/p/AF1QipMw9LPwjSWNpSQX5_3acVPv10ZTqv4Z8J6NRFkw=s1360-w1360-h1020-rw'
#      }
# ]
def home(request):
    locations = Location.objects.all()
    context = {'locations' : locations}
    return render(request, 'base/home.html', context)


def location(request, pk):
    location = Location.objects.get(name=pk)
    context = {'location': location}
    return render(request, 'base/location.html', context)

