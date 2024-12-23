import pygame

def scale_img(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def scale_finishline(img, factor):
    size = round(img.get_width() * factor), round(img.get_height())
    return pygame.transform.scale(img, size)

def blit_rotate_center(game, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center= image.get_rect(topleft = top_left).center)
    game.blit(rotated_image, new_rect.topleft)

def font_scale(size):
    return pygame.font.Font(r'fonts\PressStart2P-Regular.ttf', size)