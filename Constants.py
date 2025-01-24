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
BLUE = (0, 0, 255)
DARKGRAY = 	(20,20,20)

CAR_COLORS = {
    "Red": r"photo\car-red.png",
    "Blue": r"photo/car-blue.png",
    "Green": r"photo/car-green.png",
    "Yellow": r"photo/car-yellow.png",
    "ice": r"photo/car-ice.png",
}

LEVELS = [


{
    "track_image": r"photo\track1.png", 
    "border_image": r"photo\track1-border.png",
    "car_start_pos": (350, 200),
    "finishline_pos": [275, 250] ,
    "finishline_size": (150, 25),
    "target_time": 15.0,
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
    "target_time": 15.0,
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
    "target_time": 15.0,
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

CAR_START_POS = (350, 200)
FINISHLINE_POS = [275, 250] 
FINISHLINE_SIZE = (150, 25)
TARGET_TIME = 35.0
TRACK_BORDER = r"photo\track1-border.png"
TRACK = r"photo\track1.png"
TRACK_BONUS_POINTS = [
    (296, 119),
    (359, 120),
    (340, 93),
    (278, 78),
    (245, 64),
    (226, 103),
    (172, 82),
    (149, 133),
    (99, 140),
    (67, 153),
    (135, 197),
    (176, 190),
    (107, 249),
    (65, 266),
    (102, 238),
    (164, 300),
    (144, 329),
    (77, 326),
    (68, 340),
    (116, 396),
    (193, 429),
    (123, 441),
    (98, 495),
    (123, 542),
    (166, 547),
    (197, 543),
    (196, 614),
    (235, 584),
    (267, 605),
    (315, 625),
    (331, 671),
    (358, 652),
    (372, 692),
    (428, 683),
    (442, 729),
    (465, 707),
    (493, 758),
    (528, 736),
    (517, 778),
    (403, 720),
    (558, 763),
    (590, 809),
    (585, 819),
    (618, 769),
    (660, 810),
    (696, 827),
    (708, 780),
    (744, 786),
    (816, 792),
    (839, 755),
    (838, 743),
    (766, 734),
    (759, 695),
    (822, 682),
    (829, 650),
    (781, 621),
    (795, 606),
    (843, 570),
    (903, 558),
    (909, 576),
    (956, 536),
    (1004, 526),
    (1033, 554),
    (1099, 544),
    (1099, 544),
    (1136, 566),
    (1183, 596),
    (1188, 609),
    (1205, 618),
    (1205, 624),
    (1153, 660),
    (1164, 703),
    (1202, 741),
    (1243, 752),
    (1227, 778),
    (1220, 805),
    (1274, 824),
    (1355, 805),
    (1371, 795),
    (1380, 798),
    (1408, 800),
    (1430, 793),
    (1465, 754),
    (1472, 739),
    (1472, 738),
    (1431, 723),
    (1434, 702),
    (1447, 677),
    (1490, 660),
    (1501, 658),
    (1485, 646),
    (1428, 601),
    (1419, 590),
    (1463, 563),
    (1473, 558),
    (1475, 546),
    (1484, 540),
    (1486, 521),
    (1441, 473),
    (1438, 472),
    (1422, 460),
    (1473, 447),
    (1442, 423),
    (1356, 402),
    (1305, 422),
    (1300, 426),
    (1246, 380),
    (1204, 430),
    (1161, 426),
    (1130, 400),
    (1059, 420),
    (1029, 414),
    (1020, 406),
    (984, 386),
    (919, 424),
    (882, 411),
    (862, 393),
    (839, 377),
    (813, 344),
    (876, 288),
    (791, 390),
    (767, 333),
    (800, 290),
    (838, 334),
    (927, 275),
    (953, 320),
    (995, 275),
    (1029, 308),
    (1071, 280),
    (1102, 284),
    (1117, 292),
    (1157, 292),
    (1178, 294),
    (1209, 268),
    (1111, 311),
    (1244, 268),
    (1250, 313),
    (1286, 280),
    (1212, 313),
    (1346, 266),
    (1362, 309),
    (1448, 281),
    (1487, 250),
    (1388, 233),
    (1506, 207),
    (1417, 260),
    (1436, 186),
    (1399, 176),
    (1508, 125),
    (1434, 113),
    (1479, 169),
    (1405, 109),
    (1403, 81),
    (1313, 101),
    (1284, 61),
    (1244, 109),
    (1208, 63),
    (1168, 98),
    (1130, 63),
    (1077, 101),
    (1055, 70),
    (1013, 99),
    (980, 82),
    (933, 94),
    (897, 79),
    (863, 95),
    (831, 60),
    (797, 102),
    (769, 78),
    (717, 94),
    (682, 62),
    (659, 96),
    (626, 106),
    (601, 89),
    (552, 129),
    (585, 158),
    (519, 191),
    (579, 206),
    (512, 236),
    (559, 264),
    (522, 295),
    (610, 308),
    (523, 358),
    (585, 366),
    (535, 393),
    (565, 426),
    (508, 448),
    (514, 452),
    (408, 465),
    (450, 431),
    (344, 457),
    (363, 413),
    (392, 389),
    (305, 396),
    (363, 358),
    (386, 341),
]

BOMB = r'photo\bomb.png'

FONT = r"fonts\Default.otf"
SPEEDOMETERFONT = r'fonts\speedometer.ttf'
COUNTDOWN_FONT = r'fonts\CountDownFont.otf'

MAXSPEED = 6.0
ROTATESPEED = 5.0
ACCELERATION = 0.12

# Assets
FINISHLINE = r'photo/finish.png'
GRASS = r'photo\grass2.jpg'
CHECKPOINT = r'photo\checkpoint.jpg'
LOBBY_VIDEO = r'video\lobby_music2.mp4'

# Sound
WIN_SOUND = r'sound/victory.wav'
COUNTDOWN_SOUND = r'sound/countdown.mp3'
BACKGROUND_MUSIC = r'sound/background_music.mp3'
COLLIDE_SOUND = r'sound/collide.mp3'
CHECKPOINT_SOUND = r'sound\CHECKPOINT_SOUND.mp3'
LOBBY_MUSIC = r'sound\lobby_music2.mp3'
OBSTACLE_SOUND = r'sound\obstacle_sound.mp3'