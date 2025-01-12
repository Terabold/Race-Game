FPS = 60
WIDTH, HEIGHT = 1600, 900

# Colors
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)
FOGGRAY = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DODGERBLUE = (30, 144, 255)
ORANGE = (255, 165, 0)
DARKORANGE = (255, 140, 0)
DARKGREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
CAR_COLORS = {
    "Red": r"photo/red-car.png",
    "Blue": r"photo/car-blue.png",
    "Green": r"photo/green-car.png",
    "Yellow": r"photo/car.png",
    "ice": r"photo/ice-car.png",
}

LEVELS = [
{
    "track_image": r"photo\track1.png", 
    "border_image": r"photo\track1-border.png",
    "car_start_pos": (350, 200),
    "finishline_pos": [275, 250] ,
    "finishline_size": (150, 25),
    "target_time": 19.0,
    "Level": "Beginner's Path",
    "checkpoints": [
        {"pos": [40, 200], "size": (170, 20)}, 
        {"pos": [700, 700], "size": (200, 20)},  
        {"pos": [1380, 600], "size": (180, 20)},  
        {"pos": [1050, 245], "size": (20, 100)},  
        {"pos": [1380, 190], "size": (170, 20)}, 
        {"pos": [735, 40], "size": (20, 100)}, 
        {"pos": [470, 250], "size": (170, 20)}, 
    ],
},
{
    "track_image": r"photo\track2.png",
    "border_image": r"photo\track2-border.png",
    "car_start_pos": (400, 240),
    "finishline_pos": [300, 300],
    "finishline_size": (200, 25),
    "target_time": 20.0,
    "Level": "Challenger's Trial" ,
    "checkpoints": [
        {"pos": [75, 260], "size": (170, 20)},  
        {"pos": [600, 700], "size": (20, 120)},  
        {"pos": [1380, 600], "size": (170, 20)},  
        {"pos": [1040, 460], "size": (20, 150)},  
        {"pos": [1320, 160], "size": (170, 20)},  
        {"pos": [505, 360], "size": (170, 20)}, 
    ],
},
{
    "track_image": r"photo\track3.png",
    "border_image": r"photo\track3-border.png",
    "car_start_pos": (380, 200),
    "finishline_pos": [295, 250],
    "finishline_size": (175, 25),
    "target_time": 17.0,
    "Level": "Adventurer's Circuit" ,
    "checkpoints": [
        {"pos": [70, 230], "size": (170, 20)}, 
        {"pos": [260, 680], "size": (20, 100)},  
        {"pos": [530, 460], "size": (20, 100)}, 
        {"pos": [1160, 560], "size": (170, 20)},  
        {"pos": [1380, 460], "size": (170, 20)},  
        {"pos": [700, 320], "size": (20, 100)},  
    ],
},
{
    "track_image": r"photo\track4.png",
    "border_image": r"photo\track4-border.png",
    "car_start_pos": (510, 275),
    "finishline_pos": [460, 325],
    "finishline_size": (120, 25),
    "target_time": 17.0,
    "Level": "Elite Driver's Course" ,
    "checkpoints": [
        {"pos": [255, 70], "size": (20, 150)}, 
        {"pos": [540, 690], "size": (20, 150)},  
        {"pos": [1075, 280], "size": (20, 150)},  
        {"pos": [1420, 480], "size": (150, 20)},  
        {"pos": [1050, 70], "size": (20, 150)},  
        {"pos": [680, 500], "size": (20, 150)},  
    ],
},
{
    "track_image": r"photo\track5.png",
    "border_image": r"photo\track5-border.png",
    "car_start_pos": (570, 175),
    "finishline_pos": [500, 220],
    "finishline_size": (135, 25),
    "target_time": 20.0,
    "Level": "Master's Challenge" ,
    "checkpoints": [
        {"pos": [300, 230], "size": (170, 20)},  
        {"pos": [80, 600], "size": (170, 20)},  
        {"pos": [430, 580], "size": (170, 20)},  
        {"pos": [1200, 540], "size": (170, 20)}, 
        {"pos": [1000, 780], "size": (20, 100)}, 
        {"pos": [1390, 400], "size": (170, 20)}, 
        {"pos": [890, 230], "size": (170, 20)}, 
    ],
},
]

# Track bonus point positions
track1_points = [

    (305, 255),
    (378, 223),
    (292, 155),
    (346, 99),
    (221, 75),
    (189, 122),
    (122, 84),
    (86, 163),
    (164, 169),
    (97, 291),
    (163, 297),
    (101, 394),
    (107, 481),
    (158, 397),
    (171, 538),
    (205, 595),
    (283, 584),
    (361, 681),
    (463, 735),
    (547, 732),
    (608, 803),
    (709, 819),
    (752, 718),
    (818, 713),
    (829, 575),
    (938, 532),
    (1001, 559),
    (1135, 538),
    (1159, 654),
    (1286, 798),
    (1412, 782),
    (1405, 710),
    (1497, 688),
    (1192, 760),
    (1420, 600),
    (1476, 549),
    (1425, 496),
    (1470, 427),
    (1306, 404),
    (1157, 420),
    (993, 396),
    (788, 412),
    (824, 338),
    (921, 276),
    (1006, 304),
    (1232, 268),
    (1121, 307),
    (1394, 283),
    (1404, 228),
    (1490, 175),
    (1370, 94),
    (1123, 103),
    (972, 74),
    (1252, 89),
    (819, 74),
    (643, 114),
    (515, 159),
    (598, 328),
    (520, 257),
    (534, 412),
    (426, 453),
    (376, 361),
    (304, 381),
]
  # Will be populated by point collector

track2_points = [
    (296, 106),
    (125, 176),
    (163, 324),
    (98, 494),
    (197, 593),
    (274, 707),
    (515, 740),
    (630, 783),
    (923, 712),
    (1016, 670),
    (767, 761),
    (1207, 747),
    (1400, 798),
    (1504, 672),
    (1412, 455),
    (1213, 414),
    (1097, 526),
    (937, 477),
    (809, 379),
    (934, 244),
    (1121, 255),
    (1316, 205),
    (1356, 261),
    (1037, 222),
    (1410, 132),
    (1168, 75),
    (1065, 130),
    (899, 91),
    (750, 155),
    (609, 212),
    (631, 368),
    (546, 472),
    (398, 523),
    (438, 378),
]

track3_points = [
    (351, 132),
    (211, 109),
    (117, 204),
    (185, 282),
    (108, 383),
    (169, 515),
    (112, 602),
    (178, 729),
    (314, 700),
    (398, 584),
    (399, 677),
    (474, 500),
    (660, 553),
    (710, 719),
    (881, 737),
    (974, 573),
    (1175, 499),
    (942, 645),
    (1253, 590),
    (1181, 695),
    (1280, 802),
    (1465, 714),
    (1435, 559),
    (1451, 422),
    (1297, 375),
    (1110, 363),
    (970, 387),
    (870, 348),
    (716, 387),
    (651, 351),
    (501, 381),
    (427, 305),
    (1159, 767),
    (1419, 784),
    (1081, 504),
    (680, 637),
    (581, 507),
    (173, 386),
    (93, 273),
]

track4_points = [
    (333, 151),
    (146, 158),
    (145, 294),
    (114, 500),
    (240, 606),
    (372, 730),
    (575, 744),
    (748, 799),
    (849, 730),
    (1006, 698),
    (984, 541),
    (1044, 358),
    (1011, 455),
    (1182, 433),
    (1140, 603),
    (1223, 687),
    (1396, 702),
    (1389, 786),
    (1467, 532),
    (1490, 340),
    (1483, 655),
    (1444, 266),
    (1415, 130),
    (1233, 181),
    (1170, 101),
    (1005, 160),
    (1071, 110),
    (1112, 172),
    (939, 119),
    (885, 171),
    (830, 305),
    (855, 461),
    (765, 546),
    (629, 561),
    (538, 493),
    (500, 176),
    (221, 146),
]

track5_points = [
    (507, 73),
    (390, 89),
    (361, 183),
    (416, 249),
    (306, 330),
    (174, 349),
    (123, 507),
    (166, 505),
    (135, 700),
    (187, 787),
    (330, 819),
    (136, 622),
    (424, 781),
    (488, 702),
    (495, 589),
    (548, 473),
    (666, 455),
    (849, 440),
    (971, 428),
    (1066, 452),
    (1221, 444),
    (1220, 535),
    (1281, 563),
    (1051, 669),
    (991, 643),
    (1174, 630),
    (820, 672),
    (836, 754),
    (760, 769),
    (916, 830),
    (1093, 811),
    (1209, 833),
    (1351, 800),
    (1436, 770),
    (1492, 674),
    (1418, 563),
    (1469, 509),
    (1429, 400),
    (1473, 350),
    (1428, 258),
    (1462, 209),
    (1362, 152),
    (1232, 138),
    (1165, 142),
    (1087, 154),
    (1005, 164),
    (958, 209),
    (1036, 251),
    (954, 304),
    (813, 318),
    (666, 305),
    (573, 268),
]


TRACK_BONUS_POINTS = {
    "track1": track1_points,
    "track2": track2_points,
    "track3": track3_points,
    "track4": track4_points,
    "track5": track5_points
}

FONT = r"fonts\Default.otf"
SPEEDOMETERFONT = r'fonts\speedometer.ttf'
COUNTDOWN_FONT = r'fonts\CountDownFont.otf'

MAXSPEED = 5
ROTATESPEED = 5
ACCELERATION = 0.12

# Assets
CAR_IMG = r"photo/car.png"
FINISHLINE = r'photo/finish.png'
GRASS = r'photo\grass2.jpg'
CHECKPOINT = r'photo\checkpoint.jpg'
MENU = r'photo\menu.jpg'
LOBBY_VIDEO = r'video\background_video.mp4'

# Sound
WIN_SOUND = r'sound/victory.wav'
COUNTDOWN_SOUND = r'sound/countdown.mp3'
BACKGROUND_MUSIC = r'sound/background_music.mp3'
COLLIDE_SOUND = r'sound/collide.mp3'
CHECKPOINT_SOUND = r'sound\CHECKPOINT_SOUND.mp3'
LOBBY_MUSIC = r'sound\lobby_music2.mp3'
TIME_BONUS_SOUND = r'sound\timerbonussound.mp3'