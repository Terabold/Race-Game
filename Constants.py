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
    "target_time": 15.0,
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
    "target_time": 15.0,
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

track2_points = [
    (363, 175),
    (397, 150),
    (376, 107),
    (408, 96),
    (353, 122),
    (323, 83),
    (302, 127),
    (271, 80),
    (265, 120),
    (211, 79),
    (202, 131),
    (156, 96),
    (119, 173),
    (201, 169),
    (109, 199),
    (160, 230),
    (148, 259),
    (132, 286),
    (159, 301),
    (146, 323),
    (102, 364),
    (168, 381),
    (198, 411),
    (130, 453),
    (99, 489),
    (167, 496),
    (160, 530),
    (142, 573),
    (172, 622),
    (216, 656),
    (255, 671),
    (288, 697),
    (310, 721),
    (311, 751),
    (238, 712),
    (224, 641),
    (186, 588),
    (180, 656),
    (118, 549),
    (168, 452),
    (134, 396),
    (337, 367),
    (420, 350),
    (436, 371),
    (371, 422),
    (403, 437),
    (341, 475),
    (367, 495),
    (407, 533),
    (458, 531),
    (482, 527),
    (550, 541),
    (586, 492),
    (554, 486),
    (648, 451),
    (578, 431),
    (620, 400),
    (561, 381),
    (640, 336),
    (565, 333),
    (616, 292),
    (588, 263),
    (663, 190),
    (700, 234),
    (626, 221),
    (704, 136),
    (744, 123),
    (758, 151),
    (800, 86),
    (836, 121),
    (886, 83),
    (916, 122),
    (994, 72),
    (1023, 109),
    (1063, 79),
    (980, 101),
    (1164, 84),
    (1140, 117),
    (1103, 92),
    (1210, 99),
    (1250, 81),
    (1262, 122),
    (1338, 83),
    (1375, 101),
    (1353, 134),
    (1416, 142),
    (1373, 195),
    (1417, 203),
    (1352, 243),
    (1275, 240),
    (1247, 216),
    (1213, 261),
    (1162, 221),
    (1106, 262),
    (1088, 230),
    (1015, 242),
    (955, 256),
    (917, 247),
    (867, 297),
    (776, 334),
    (834, 360),
    (860, 406),
    (860, 400),
    (867, 439),
    (926, 466),
    (937, 496),
    (966, 491),
    (1055, 482),
    (1075, 528),
    (1120, 500),
    (1145, 469),
    (1164, 482),
    (1202, 438),
    (1236, 429),
    (1264, 447),
    (1288, 394),
    (1331, 409),
    (1368, 442),
    (1442, 429),
    (1470, 457),
    (1442, 512),
    (1464, 551),
    (1448, 598),
    (1464, 653),
    (1472, 700),
    (1427, 733),
    (1437, 807),
    (1466, 762),
    (1419, 619),
    (1486, 584),
    (1013, 537),
    (860, 487),
    (802, 433),
    (822, 318),
    (875, 363),
    (1352, 785),
    (1316, 813),
    (1251, 735),
    (1203, 789),
    (1186, 700),
    (1127, 756),
    (1074, 690),
    (1041, 710),
    (967, 672),
    (929, 739),
    (883, 741),
    (786, 734),
    (715, 785),
    (679, 770),
    (595, 755),
    (532, 760),
    (448, 749),
    (419, 765),
    (389, 734),
    (470, 766),
    (518, 737),
    (641, 736),
    (615, 777),
    (726, 742),
    (793, 769),
    (860, 728),
    (892, 686),
    (511, 559),
    (902, 504),
    (1211, 747),
    (1122, 688),
    (1010, 671),
    (976, 716),
    (1271, 788),
    (1402, 779),
]

track3_points = [
    (342, 147),
    (398, 119),
    (265, 97),
    (259, 79),
    (289, 117),
    (288, 90),
    (183, 119),
    (160, 88),
    (132, 141),
    (207, 140),
    (130, 196),
    (174, 210),
    (108, 236),
    (197, 232),
    (138, 278),
    (180, 304),
    (106, 333),
    (164, 333),
    (146, 357),
    (182, 371),
    (122, 415),
    (159, 424),
    (175, 432),
    (142, 457),
    (90, 477),
    (198, 477),
    (171, 500),
    (136, 527),
    (169, 538),
    (102, 582),
    (156, 583),
    (147, 606),
    (159, 640),
    (103, 678),
    (193, 668),
    (177, 730),
    (230, 727),
    (255, 711),
    (308, 730),
    (328, 677),
    (362, 693),
    (392, 690),
    (400, 657),
    (423, 619),
    (369, 616),
    (346, 585),
    (371, 555),
    (419, 510),
    (455, 519),
    (492, 513),
    (540, 504),
    (597, 511),
    (649, 517),
    (686, 525),
    (644, 567),
    (688, 581),
    (723, 609),
    (669, 644),
    (709, 648),
    (668, 673),
    (732, 703),
    (764, 724),
    (692, 732),
    (662, 726),
    (797, 722),
    (871, 709),
    (803, 740),
    (781, 747),
    (886, 732),
    (877, 678),
    (927, 681),
    (966, 654),
    (946, 623),
    (938, 600),
    (993, 581),
    (1026, 568),
    (1040, 548),
    (1011, 529),
    (1070, 502),
    (1130, 502),
    (1151, 513),
    (1130, 536),
    (1218, 520),
    (1213, 552),
    (1265, 558),
    (1238, 584),
    (1269, 598),
    (1213, 637),
    (1255, 655),
    (1183, 688),
    (1175, 704),
    (1174, 630),
    (1178, 642),
    (1205, 722),
    (1168, 753),
    (1162, 767),
    (1211, 770),
    (1253, 787),
    (1123, 721),
    (1291, 778),
    (1293, 798),
    (1336, 794),
    (1355, 758),
    (1397, 792),
    (1451, 758),
    (1408, 725),
    (1487, 699),
    (1416, 689),
    (1489, 651),
    (1396, 649),
    (1468, 621),
    (1428, 619),
    (1465, 570),
    (1404, 579),
    (1481, 546),
    (1434, 536),
    (1466, 504),
    (1481, 480),
    (1450, 424),
    (1468, 410),
    (1390, 474),
    (1436, 469),
    (1410, 413),
    (1398, 375),
    (1361, 393),
    (1327, 360),
    (1296, 371),
    (1251, 381),
    (1220, 355),
    (1176, 390),
    (1122, 356),
    (1063, 399),
    (1046, 372),
    (1001, 364),
    (923, 379),
    (897, 368),
    (869, 375),
    (844, 373),
    (760, 361),
    (719, 390),
    (723, 359),
    (791, 390),
    (807, 355),
    (640, 381),
    (635, 348),
    (675, 359),
    (669, 388),
    (579, 364),
    (553, 338),
    (509, 370),
    (485, 372),
    (425, 368),
    (1109, 379),
    (1178, 351),
]

track4_points = [
    (466, 218),
    (476, 135),
    (427, 131),
    (392, 163),
    (369, 113),
    (320, 134),
    (282, 124),
    (269, 134),
    (210, 151),
    (187, 117),
    (150, 174),
    (302, 161),
    (369, 133),
    (303, 164),
    (176, 194),
    (155, 224),
    (112, 265),
    (140, 293),
    (139, 339),
    (113, 373),
    (147, 408),
    (129, 450),
    (146, 489),
    (148, 524),
    (148, 585),
    (189, 559),
    (215, 629),
    (244, 614),
    (296, 623),
    (331, 670),
    (268, 680),
    (371, 699),
    (395, 728),
    (425, 691),
    (452, 766),
    (492, 744),
    (535, 710),
    (550, 768),
    (599, 766),
    (627, 712),
    (634, 768),
    (674, 745),
    (707, 772),
    (741, 728),
    (760, 772),
    (793, 745),
    (821, 752),
    (840, 750),
    (874, 749),
    (889, 740),
    (939, 714),
    (948, 664),
    (997, 711),
    (1026, 625),
    (1001, 577),
    (911, 780),
    (973, 669),
    (999, 589),
    (986, 511),
    (990, 439),
    (1019, 390),
    (1040, 365),
    (1013, 455),
    (999, 494),
    (1093, 369),
    (1120, 355),
    (1126, 423),
    (1166, 410),
    (1162, 481),
    (1137, 561),
    (1196, 545),
    (1173, 604),
    (1171, 645),
    (1193, 666),
    (1235, 678),
    (1204, 767),
    (1214, 756),
    (1191, 700),
    (1193, 694),
    (1293, 732),
    (1324, 782),
    (1343, 735),
    (1367, 784),
    (1413, 713),
    (1440, 729),
    (1482, 642),
    (1454, 626),
    (1507, 561),
    (1499, 537),
    (1459, 513),
    (1472, 469),
    (1454, 451),
    (1480, 424),
    (1483, 394),
    (1438, 368),
    (1476, 343),
    (1499, 325),
    (1478, 312),
    (1498, 257),
    (1442, 253),
    (1476, 229),
    (1487, 220),
    (1425, 201),
    (1443, 153),
    (1411, 212),
    (1381, 136),
    (1300, 116),
    (1291, 174),
    (1284, 127),
    (1214, 164),
    (1168, 129),
    (1134, 168),
    (1113, 135),
    (995, 134),
    (978, 165),
    (922, 140),
    (865, 179),
    (837, 198),
    (882, 230),
    (835, 329),
    (827, 273),
    (834, 285),
    (867, 370),
    (829, 393),
    (820, 410),
    (849, 450),
    (835, 487),
    (788, 522),
    (769, 567),
    (717, 563),
    (691, 594),
    (677, 538),
    (646, 595),
    (628, 557),
    (599, 542),
    (571, 548),
    (588, 521),
    (584, 596),
    (501, 195),
    (457, 178),
    (524, 510),
    (575, 494),
    (548, 518),
    (1042, 169),
    (1068, 119),
    (1191, 101),
    (1192, 141),
    (1243, 125),
    (1363, 170),
    (1183, 522),
    (1287, 774),
    (1439, 700),
    (1409, 741),
    (1475, 559),
    (955, 758),
    (587, 743),
    (668, 724),
    (836, 779),
    (219, 583),
    (105, 326),
]

track5_points = [
    (541, 138),
    (573, 82),
    (494, 64),
    (445, 103),
    (425, 77),
    (351, 93),
    (336, 148),
    (399, 165),
    (352, 199),
    (352, 259),
    (377, 276),
    (335, 314),
    (267, 322),
    (217, 328),
    (193, 355),
    (167, 354),
    (122, 406),
    (192, 439),
    (118, 489),
    (136, 510),
    (149, 523),
    (131, 566),
    (174, 578),
    (161, 644),
    (153, 708),
    (161, 717),
    (145, 758),
    (207, 791),
    (289, 806),
    (322, 821),
    (423, 813),
    (449, 785),
    (459, 765),
    (493, 710),
    (525, 658),
    (486, 646),
    (522, 595),
    (492, 570),
    (521, 523),
    (536, 485),
    (583, 446),
    (621, 435),
    (678, 446),
    (730, 435),
    (772, 438),
    (839, 417),
    (886, 437),
    (963, 431),
    (972, 447),
    (1033, 435),
    (1055, 441),
    (1130, 440),
    (1178, 440),
    (1219, 464),
    (1249, 492),
    (1303, 512),
    (1264, 547),
    (1271, 580),
    (1259, 616),
    (1192, 645),
    (1141, 633),
    (1104, 650),
    (1055, 647),
    (979, 645),
    (919, 643),
    (855, 677),
    (814, 677),
    (811, 712),
    (815, 759),
    (832, 771),
    (856, 817),
    (922, 815),
    (977, 814),
    (1037, 819),
    (1089, 823),
    (1130, 810),
    (1196, 800),
    (1243, 828),
    (1270, 813),
    (1314, 811),
    (1348, 801),
    (1385, 800),
    (1465, 738),
    (1438, 737),
    (1434, 772),
    (1478, 743),
    (1484, 681),
    (1419, 692),
    (1462, 649),
    (1441, 645),
    (1464, 612),
    (1476, 577),
    (1434, 572),
    (1455, 558),
    (1481, 522),
    (1486, 497),
    (1445, 506),
    (1431, 538),
    (1470, 522),
    (1501, 454),
    (1424, 464),
    (1463, 421),
    (1467, 429),
    (1497, 376),
    (1413, 369),
    (1462, 361),
    (1456, 354),
    (1445, 324),
    (1489, 301),
    (1474, 275),
    (1475, 260),
    (1411, 260),
    (1471, 215),
    (1428, 219),
    (1468, 199),
    (1426, 160),
    (1334, 172),
    (1335, 152),
    (1365, 148),
    (1380, 164),
    (1287, 127),
    (1277, 164),
    (1234, 145),
    (1215, 143),
    (1184, 145),
    (1154, 145),
    (1125, 154),
    (1074, 163),
    (1055, 167),
    (1021, 154),
    (1022, 146),
    (1120, 134),
    (1180, 157),
    (966, 186),
    (1022, 204),
    (1019, 234),
    (967, 253),
    (983, 281),
    (978, 309),
    (912, 313),
    (817, 316),
    (836, 329),
    (876, 307),
    (763, 346),
    (766, 302),
    (685, 331),
    (678, 330),
    (678, 315),
    (743, 309),
    (934, 291),
    (998, 210),
    (1014, 272),
    (1223, 580),
    (1212, 619),
    (481, 515),
    (512, 730),
    (500, 673),
    (366, 806),
    (256, 837),
    (181, 672),
    (112, 648),
    (169, 538),
    (152, 454),
    (194, 387),
    (276, 341),
    (304, 354),
    (387, 294),
    (382, 237),
    (330, 249),
    (380, 139),
    (386, 89),
    (605, 312),
    (1450, 698),
    (1204, 831),
    (1155, 809),
    (1048, 840),
    (964, 829),
    (1032, 803),
    (888, 656),
    (1017, 636),
    (1016, 674),
    (950, 658),
    (1302, 567),
    (1231, 510),
    (1404, 805),
    (1401, 764),
    (1444, 269),
]


TRACK_BONUS_POINTS = {
    "track1": track1_points,
    "track2": track2_points,
    "track3": track3_points,
    "track4": track4_points,
    "track5": track5_points
}

TIME_BONUS_IMAGE = r'photo\time-bonus-icon.svg'
FONT = r"fonts\Default.otf"
SPEEDOMETERFONT = r'fonts\speedometer.ttf'
COUNTDOWN_FONT = r'fonts\CountDownFont.otf'

MAXSPEED = 5.0
ROTATESPEED = 5.0
ACCELERATION = 0.12

# Assets
FINISHLINE = r'photo/finish.png'
GRASS = r'photo\grass2.jpg'
CHECKPOINT = r'photo\checkpoint.jpg'
MENU = r'photo\menu.jpg'
LOBBY_VIDEO = r'video\lobby_music2.mp4'

# Sound
WIN_SOUND = r'sound/victory.wav'
COUNTDOWN_SOUND = r'sound/countdown.mp3'
BACKGROUND_MUSIC = r'sound/background_music.mp3'
COLLIDE_SOUND = r'sound/collide.mp3'
CHECKPOINT_SOUND = r'sound\CHECKPOINT_SOUND.mp3'
LOBBY_MUSIC = r'sound\lobby_music2.mp3'
TIME_BONUS_SOUND = r'sound\timerbonussound.mp3'