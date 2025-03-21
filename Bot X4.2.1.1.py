#!/bin/bash

# Функція для виконання команд із перевіркою помилок
run_command() {
    echo "Виконую: $1"
    eval "$1"
    if [ $? -ne 0 ]; then
        echo "Помилка при виконанні: $1"
        exit 1
    fi
}

echo "Оновлення системи..."
run_command "sudo pacman -Syu --noconfirm"

echo "Встановлення базових утиліт..."
run_command "sudo pacman -S --noconfirm base-devel git wget curl sudo ccat xorg xorg-xinit"

# Визначення відеокарти та встановлення відповідних драйверів
GPU=$(lspci | grep -E "VGA|3D")
if echo "$GPU" | grep -qi "Intel"; then
    run_command "sudo pacman -S --noconfirm xf86-video-intel"
elif echo "$GPU" | grep -qi "NVIDIA"; then
    run_command "sudo pacman -S --noconfirm nvidia nvidia-utils"
elif echo "$GPU" | grep -qi "AMD"; then
    run_command "sudo pacman -S --noconfirm xf86-video-amdgpu"
fi

echo "Встановлення дисплейного менеджера (LightDM)..."
run_command "sudo pacman -S --noconfirm lightdm lightdm-gtk-greeter"
run_command "sudo systemctl enable lightdm"

echo "Встановлення Openbox та необхідних пакетів..."
run_command "sudo pacman -S --noconfirm openbox obconf lxappearance pcmanfm alacritty geany rofi network-manager-applet pulseaudio pavucontrol feh"

echo "Завантаження та налаштування Openbox теми ArchCraft..."
run_command "git clone https://github.com/archcraft-os/archcraft-openbox ~/.config/openbox"
run_command "cp -r ~/.config/openbox/* ~/.config/"
run_command "rm -rf ~/.config/openbox"

# Створення sudo-користувача
echo "Створення sudo-користувача..."
read -p "Введіть ім'я sudo-користувача: " SUDO_USER
read -s -p "Введіть пароль для sudo-користувача: " SUDO_PASS
echo
run_command "sudo useradd -m -G wheel -s /bin/bash $SUDO_USER"
echo "$SUDO_USER:$SUDO_PASS" | sudo chpasswd

# Додавання користувача до sudoers
echo "Додаємо $SUDO_USER до sudoers..."
run_command "echo '$SUDO_USER ALL=(ALL) ALL' | sudo tee -a /etc/sudoers"

# Створення звичайного користувача
echo "Створення звичайного користувача..."
read -p "Введіть ім'я звичайного користувача: " REGULAR_USER
read -s -p "Введіть пароль для звичайного користувача: " REGULAR_PASS
echo
run_command "sudo useradd -m -s /bin/bash $REGULAR_USER"
echo "$REGULAR_USER:$REGULAR_PASS" | sudo chpasswd

echo "Установка завершена! Перезавантажте систему для застосування змін."

