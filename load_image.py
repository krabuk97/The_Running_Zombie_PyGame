import pygame


class LoadImage:
    icon = pygame.image.load("image/icon1.png")

    background1 = pygame.image.load('image/background.jpg')

    menu_image = pygame.image.load('image/menu_image.jpeg')

    start_button = pygame.image.load('image/start_button.png')

    exit_button = pygame.image.load('image/exit_button.png')

    restart_button = pygame.image.load('image/restart_button.png')

    playerwalk = [
        "image/Walk/w0.png",
        "image/Walk/w1.png",
        "image/Walk/w3.png",
        "image/Walk/w4.png",
        "image/Walk/w5.png",
        "image/Walk/w6.png",
        "image/Walk/w7.png",
        "image/Walk/w8.png"
    ]

    playerstand = [
        'image/Idle/idle (1).png',
        'image/Idle/idle (2).png',
        'image/Idle/idle (3).png',
        'image/Idle/idle (4).png',
        'image/Idle/idle (5).png',
        'image/Idle/idle (6).png',
        'image/Idle/idle (7).png',
        'image/Idle/idle (8).png',
        'image/Idle/idle (9).png',
        'image/Idle/idle (10).png',
        'image/Idle/idle (11).png',
        'image/Idle/idle (12).png',
    ]

    playerdie = [
        'image/Die/die (1).png',
        'image/Die/die (2).png',
        'image/Die/die (3).png',
        'image/Die/die (4).png',
        'image/Die/die (5).png',
        'image/Die/die (6).png',
        'image/Die/die (7).png',
        'image/Die/die (8).png'
    ]

    healthbar = pygame.image.load("image/health.png")

    explosion_files = [
        "image/explosion/tile000.png",
        "image/explosion/tile001.png",
        "image/explosion/tile002.png",
        "image/explosion/tile003.png",
        "image/explosion/tile004.png",
        "image/explosion/tile005.png",
        "image/explosion/tile006.png",
        "image/explosion/tile007.png",
        "image/explosion/tile008.png",
        "image/explosion/tile009.png",
        "image/explosion/tile010.png",
        "image/explosion/tile011.png"
    ]

    nuke = [
        r'image/nuke/image_19.png',
        r'image/nuke/image_18.png',
        r'image/nuke/image_17.png',
        r'image/nuke/image_16.png',
        r'image/nuke/image_15.png',
        r'image/nuke/image_14.png',
        r'image/nuke/image_13.png',
        r'image/nuke/image_12.png',
        r'image/nuke/image_11.png',
        r'image/nuke/image_10.png',
        r'image/nuke/image_9.png',
        r'image/nuke/image_8.png',
        r'image/nuke/image_7.png',
        r'image/nuke/image_6.png',
        r'image/nuke/image_5.png',
        r'image/nuke/image_4.png',
        r'image/nuke/image_3.png',
        r'image/nuke/image_2.png'
    ]

    death_screen = pygame.image.load("image/death_screen.jpeg")

    frozen_bomb = [
        r'image/frozen/fb1.png',
        r'image/frozen/fb2.png',
        r'image/frozen/fb3.png',
        r'image/frozen/fb4.png',
        r'image/frozen/fb5.png',
        r'image/frozen/fb6.png',
        r'image/frozen/fb7.png',
        r'image/frozen/fb8.png',
        r'image/frozen/fb9.png',
        r'image/frozen/fb10.png',
        r'image/frozen/fb11.png',
        r'image/frozen/fb12.png',
    ]

    poison_bomb = [
        'image/poison/1.png',
        'image/poison/2.png',
        'image/poison/3.png',
        'image/poison/4.png',
        'image/poison/5.png',
        'image/poison/6.png',
        'image/poison/7.png'
    ]

    burn = [
        f"image/fire/frame_{frame_index:02d}_delay-0.03s.png" for frame_index in range(54)
    ]

    zombie_friend_dead = ["image/z_f/Dead/__Zombie01_Dead_000.png",
                          "image/z_f/Dead/__Zombie01_Dead_001.png",
                          "image/z_f/Dead/__Zombie01_Dead_002.png",
                          "image/z_f/Dead/__Zombie01_Dead_003.png",
                          "image/z_f/Dead/__Zombie01_Dead_004.png",
                          "image/z_f/Dead/__Zombie01_Dead_005.png",
                          "image/z_f/Dead/__Zombie01_Dead_006.png",
                          "image/z_f/Dead/__Zombie01_Dead_007.png"
                          ]

    zombie_friend_walk = ["image/z_f/Walk/__Zombie01_Walk_000.png",
                          "image/z_f/Walk/__Zombie01_Walk_001.png",
                          "image/z_f/Walk/__Zombie01_Walk_002.png",
                          "image/z_f/Walk/__Zombie01_Walk_003.png",
                          "image/z_f/Walk/__Zombie01_Walk_004.png",
                          "image/z_f/Walk/__Zombie01_Walk_005.png",
                          "image/z_f/Walk/__Zombie01_Walk_006.png",
                          "image/z_f/Walk/__Zombie01_Walk_007.png",
                          "image/z_f/Walk/__Zombie01_Walk_008.png",
                          "image/z_f/Walk/__Zombie01_Walk_009.png"
                          ]

    zombie_friend_idle = [
        "image/z_f/Idle/__Zombie01_Idle_000.png",
        "image/z_f/Idle/__Zombie01_Idle_001.png",
        "image/z_f/Idle/__Zombie01_Idle_002.png",
        "image/z_f/Idle/__Zombie01_Idle_003.png",
        "image/z_f/Idle/__Zombie01_Idle_004.png",
        "image/z_f/Idle/__Zombie01_Idle_005.png",
        "image/z_f/Idle/__Zombie01_Idle_006.png",
        "image/z_f/Idle/__Zombie01_Idle_007.png",
        "image/z_f/Idle/__Zombie01_Idle_008.png",
        "image/z_f/Idle/__Zombie01_Idle_009.png",
    ]
