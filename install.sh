#!/bin/bash

# Gerekli Python kütüphanelerini kur
pip install -r requirements.txt

# LLVM'yi yükle
if ! command -v llvm-config &> /dev/null
then
    echo "LLVM bulunamadı, lütfen LLVM'yi yükleyin."
    exit
fi

echo "Kurulum tamamlandı!"
