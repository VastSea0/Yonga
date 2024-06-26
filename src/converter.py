# Öncelikle, print fonksiyonunu yedekleyelim
eski_print = print

# Sonra yazdir isimli yeni bir fonksiyon tanımlayalım
def yazdir(*args, **kwargs):
    eski_print(*args, **kwargs)

# Artık yazdir fonksiyonunu kullanarak ekrana yazdırabiliriz
