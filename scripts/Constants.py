import numpy as np
import pygame

pygame.init()
info = pygame.display.Info()

# Display settings
REFERENCE_SIZE = (1920, 1080)
screen_width, screen_height = info.current_w, info.current_h
aspect_x = screen_width - (screen_width % 16)
aspect_y = screen_height - (screen_height % 9)
DISPLAY_SIZE = (aspect_x, aspect_y)
FPS = 60
WIDTH, HEIGHT = 1600, 900
MENUWIDTH, MENUHEIGHT = 1280, 720

# Colors
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DODGERBLUE = (30, 144, 255)
DARKGREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARKGRAY = (20, 20, 20)
ORANGE = (255, 165, 0)

#checkpoint colors
BRIGHT_GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)  
GRAY_COLOR = (100, 100, 100)

# Car colors mapping
CAR_COLORS = {
    "Red": r"data\photo\car-red.png",
    "Blue": r"data\photo/car-blue.png",
    "Black": r"data\photo/car-black.png",
    "Yellow": r"data\photo/car-yellow.png",
    "White": r"data\photo/car-white.png",
}

# Game settings
CAR_START_POS = (350, 225)
FINISHLINE_POS = np.array([250, 250])
FINISHLINE_SIZE = (180, 25)
TARGET_TIME = 25.0

# Physics constants
MAXSPEED = 6.0
ROTATESPEED = 5.0
ACCELERATION = 0.12

# Asset paths
TRACK_BORDER = r"data\photo\track1-border.png"
TRACK = r"data\photo\trackv2.png"
BOMB = r'data\photo\bomb.png'
FINISHLINE = r'data\photo/finish.png'
GRASS = r'data\photo\grass2.jpg'
CHECKPOINT = r'data\photo\checkpoint.jpg'
MENU = r'data\photo\Background.jpg'
RECT = r'data\photo\Rect.png'
MENUBG = r'data\photo\Background.jpg'

# Fonts
FONT = r'data\fonts\Menu.ttf'
COUNTDOWN_FONT = r'data\fonts\CountDownFont.otf'
MENUFONT = r'data\fonts\Menu.ttf'

# Sound paths
WIN_SOUND = r'data\sound/victory.wav'
COUNTDOWN_SOUND = r'data\sound/countdown.mp3'
BACKGROUND_MUSIC = r'data\sound/background_music.mp3'
COLLIDE_SOUND = r'data\sound/collide.mp3'
CHECKPOINT_SOUND = r'data\sound\CHECKPOINT_SOUND.mp3'
OBSTACLE_SOUND = r'data\sound\obstacle_sound.mp3'

# Sound/UI settings
SOUND_EXTENSIONS = ('.mp3', '.wav', '.ogg')
DEFAULT_REMOVE_COLOR = (0, 0, 0)
DEFAULT_SOUND_VOLUME = 0.05
DEFAULT_HOVER_VOLUME = 0.01
DEFAULT_CLICK_VOLUME = 0.05
MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 72
BASE_IMG_PATH = 'data/images/'

TRACK_CHECKPOINT_ZONES = [
    [(260, 155), (440, 161)],  # Checkpoint 1
    [(236, 142), (235, 39)],  # Checkpoint 2
    [(216, 155), (24, 162)],  # Checkpoint 3
    [(221, 509), (65, 567)],  # Checkpoint 4
    [(678, 755), (684, 866)],  # Checkpoint 5
    [(707, 741), (893, 734)],  # Checkpoint 6
    [(807, 517), (908, 606)],  # Checkpoint 7
    [(988, 483), (985, 586)],  # Checkpoint 8
    [(1086, 613), (1227, 543)],  # Checkpoint 9
    [(1091, 729), (1273, 736)],  # Checkpoint 10
    [(1319, 755), (1326, 859)],  # Checkpoint 11
    [(1364, 738), (1552, 734)],  # Checkpoint 12
    [(1362, 466), (1554, 468)],  # Checkpoint 13
    [(1360, 466), (1348, 357)],  # Checkpoint 14
    [(891, 352), (891, 458)],  # Checkpoint 15
    [(702, 350), (889, 350)],  # Checkpoint 16
    [(886, 243), (891, 348)],  # Checkpoint 17
    [(1348, 243), (1350, 343)],  # Checkpoint 18
    [(1362, 239), (1552, 236)],  # Checkpoint 19
    [(1360, 149), (1550, 147)],  # Checkpoint 20
    [(1358, 147), (1352, 41)],  # Checkpoint 21
    [(658, 147), (658, 38)],  # Checkpoint 22
    [(461, 157), (649, 150)],  # Checkpoint 23
    [(468, 393), (658, 389)],  # Checkpoint 24
    [(457, 400), (456, 512)],  # Checkpoint 25
    [(259, 400), (461, 400)],  # Checkpoint 26
]


# Obstacle spawn points on track
TRACK_BONUS_POINTS = [
    (296, 119), (359, 120), (340, 93), (278, 78), (245, 64), (226, 103),
    (172, 82), (149, 133), (99, 140), (67, 153), (135, 197), (176, 190),
    (107, 249), (65, 266), (102, 238), (164, 300), (144, 329), (77, 326),
    (68, 340), (116, 396), (193, 429), (123, 441), (98, 495), (123, 542),
    (166, 547), (197, 543), (196, 614), (235, 584), (267, 605), (315, 625),
    (331, 671), (358, 652), (372, 692), (428, 683), (442, 729), (465, 707),
    (493, 758), (528, 736), (517, 778), (403, 720), (558, 763), (590, 809),
    (585, 819), (618, 769), (660, 810), (696, 827), (708, 780), (744, 786),
    (816, 792), (839, 755), (838, 743), (766, 734), (759, 695), (822, 682),
    (829, 650), (781, 621), (795, 606), (843, 570), (903, 558), (909, 576),
    (956, 536), (1004, 526), (1033, 554), (1099, 544), (1136, 566), (1183, 596),
    (1188, 609), (1205, 618), (1153, 660), (1164, 703), (1202, 741), (1243, 752),
    (1227, 778), (1220, 805), (1274, 824), (1355, 805), (1371, 795), (1380, 798),
    (1408, 800), (1430, 793), (1465, 754), (1472, 739), (1431, 723), (1434, 702),
    (1447, 677), (1490, 660), (1501, 658), (1485, 646), (1428, 601), (1419, 590),
    (1463, 563), (1473, 558), (1475, 546), (1484, 540), (1486, 521), (1441, 473),
    (1438, 472), (1422, 460), (1473, 447), (1442, 423), (1356, 402), (1305, 422),
    (1300, 426), (1246, 380), (1204, 430), (1161, 426), (1130, 400), (1059, 420),
    (1029, 414), (1020, 406), (984, 386), (919, 424), (882, 411), (862, 393),
    (839, 377), (813, 344), (876, 288), (791, 390), (767, 333), (800, 290),
    (838, 334), (927, 275), (953, 320), (995, 275), (1029, 308), (1071, 280),
    (1102, 284), (1117, 292), (1157, 292), (1178, 294), (1209, 268), (1111, 311),
    (1244, 268), (1250, 313), (1286, 280), (1212, 313), (1346, 266), (1362, 309),
    (1448, 281), (1487, 250), (1388, 233), (1506, 207), (1417, 260), (1436, 186),
    (1399, 176), (1508, 125), (1434, 113), (1479, 169), (1405, 109), (1403, 81),
    (1313, 101), (1284, 61), (1244, 109), (1208, 63), (1168, 98), (1130, 63),
    (1077, 101), (1055, 70), (1013, 99), (980, 82), (933, 94), (897, 79),
    (863, 95), (831, 60), (797, 102), (769, 78), (717, 94), (682, 62),
    (659, 96), (626, 106), (601, 89), (552, 129), (585, 158), (519, 191),
    (579, 206), (512, 236), (559, 264), (522, 295), (610, 308), (523, 358),
    (585, 366), (535, 393), (565, 426), (508, 448), (514, 452), (408, 465),
    (450, 431), (344, 457), (363, 413), (392, 389), (305, 396), (363, 358),
    (386, 341),
]