# notification_image.py
import os
import logging
import random
import hashlib
import re
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageFilter
from datetime import datetime

# Setup logging with UTF-8 encoding support
logger = logging.getLogger(__name__)

def generate_avatar(name: str, size: tuple = (500, 500)) -> Image.Image:
    """
    Generate a professional circular avatar from username.
    Uses hash → color + initials.
    """
    if not name or name.strip() == "":
        name = "Unknown"

    # Hash name for consistent color
    hash_obj = hashlib.md5(name.encode("utf-8"))
    color = tuple(int(hash_obj.hexdigest()[i:i+2], 16) for i in (0, 2, 4))  # RGB
    color = tuple(min(220, max(60, c)) for c in color)  # Keep it readable

    # Base image
    img = Image.new("RGBA", size, (*color, 255))
    draw = ImageDraw.Draw(img)

    # Circle background
    draw.ellipse((0, 0, size[0], size[1]), fill=(*color, 255))

    # Initials
    initials = "".join([part[0].upper() for part in name.split() if part])[:2]
    if not initials:
        initials = "U"

    try:
        # Try large font first
        font_size = 200
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default().font_variant(size=font_size // 2)

    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), initials, font=font, fill=(255, 255, 255))

    # Apply circular mask
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)

    return img

def get_profile_photo(bot, user_id):
    """Download and process profile photo - fallback to generated avatar if not available"""
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1)
        if not photos.photos:
            raise Exception("No profile photo available")
            
        file_info = bot.get_file(photos.photos[0][-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(f"{user_id}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
            
        original_img = Image.open(f"{user_id}.jpg").convert("RGB")
        
        # Create circular mask
        size = (500, 500)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        # Resize and apply mask
        img = ImageOps.fit(original_img, size, method=Image.LANCZOS)
        img.putalpha(mask)
        
        os.remove(f"{user_id}.jpg")
        return img
    except Exception as e:
        logger.warning(f"Using generated avatar for {user_id}: {e}")
        # Generate avatar based on user ID
        return generate_avatar(str(user_id))

def safe_filename(filename):
    """Convert filename to safe ASCII-only filename"""
    # Replace non-ASCII characters with underscores
    safe_name = re.sub(r'[^\x00-\x7F]+', '_', filename)
    # Remove any other problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', safe_name)
    # Limit length and remove trailing spaces/dots
    safe_name = safe_name.strip('. ')[:50]
    # If empty after cleaning, use default
    if not safe_name:
        safe_name = "user"
    return safe_name

def safe_log_message(message):
    """Safely encode message for logging"""
    try:
        return message.encode('utf-8', 'replace').decode('utf-8')
    except:
        return "Notification image generated"

def generate_notification_image(user_img, bot_img, user_name, bot_name, service_name):
    """Generate a pro-quality notification image in the style of imagen.py"""
    try:
        width, height = 1000, 500
        bg = Image.new("RGB", (width, height), (10, 15, 30))
        draw = ImageDraw.Draw(bg)

        # Gradient background
        for y in range(height):
            r = int(10 + (y/height) * 40)
            g = int(15 + (y/height) * 30)
            b = int(30 + (y/height) * 60)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Noise texture
        for _ in range(2000):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            brightness = random.randint(-10, 10)
            r, g, b = bg.getpixel((x, y))
            bg.putpixel((x, y), (
                max(0, min(255, r + brightness)),
                max(0, min(255, g + brightness)),
                max(0, min(255, b + brightness))
            ))

        # Fonts
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 46)
            name_font = ImageFont.truetype("arialbd.ttf", 32)
            service_font = ImageFont.truetype("arial.ttf", 28)
            info_font = ImageFont.truetype("arial.ttf", 22)
        except:
            title_font = ImageFont.load_default().font_variant(size=28)
            name_font = ImageFont.load_default().font_variant(size=20)
            service_font = ImageFont.load_default().font_variant(size=18)
            info_font = ImageFont.load_default().font_variant(size=16)

        # Header
        draw.rectangle([0, 0, width, 80], fill=(25, 35, 65))
        draw.rectangle([0, 75, width, 80], fill=(255, 215, 0))
        title_text = "NEW ORDER NOTIFICATION"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2 + 2, 42), title_text, font=title_font, fill=(0, 0, 0, 128))
        draw.text(((width - title_width) // 2, 40), title_text, font=title_font, fill=(255, 255, 255))

        # Cards
        card_width = 380
        card_height = 280
        card_y = 100
        card_margin = 40
        user_card_x1 = card_margin
        bot_card_x1 = width - card_margin - card_width

        draw.rounded_rectangle([user_card_x1, card_y, user_card_x1 + card_width, card_y + card_height],
                              radius=20, fill=(25, 35, 65, 200), outline=(255, 215, 0), width=3)
        draw.rounded_rectangle([bot_card_x1, card_y, bot_card_x1 + card_width, card_y + card_height],
                              radius=20, fill=(25, 35, 65, 200), outline=(100, 200, 255), width=3)

        # Profile drawer
        def draw_modern_profile(base, img, card_x, card_y, card_width, img_size, display_name, actual_name, is_bot=False):
            profile_x = card_x + (card_width - img_size) // 2
            profile_y = card_y + 40

            # Glow
            glow_size = img_size + 30
            glow = Image.new("RGBA", (glow_size, glow_size), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_color = (255, 215, 0) if not is_bot else (100, 200, 255)
            for i in range(15):
                alpha = int(100 * (1 - i/15))
                color = (*glow_color, alpha)
                glow_draw.ellipse([15-i, 15-i, glow_size-15+i, glow_size-15+i], outline=color, width=2)
            glow = glow.filter(ImageFilter.GaussianBlur(3))
            base.paste(glow, (profile_x-15, profile_y-15), glow)

            # Image + border
            img_resized = img.resize((img_size, img_size))
            mask = Image.new('L', (img_size, img_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, img_size, img_size), fill=255)
            img_rgba = img_resized.convert('RGBA')
            img_rgba.putalpha(mask)

            border_color = (255, 215, 0) if not is_bot else (100, 200, 255)
            border_img = Image.new('RGBA', (img_size + 8, img_size + 8), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_img)
            border_draw.ellipse((0, 0, img_size + 7, img_size + 7), outline=border_color, width=4)
            border_img.paste(img_rgba, (4, 4), img_rgba)
            base.paste(border_img, (profile_x, profile_y), border_img)

            # Labels
            display_bg = Image.new('RGBA', (card_width - 20, 30), (0, 0, 0, 180))
            d_draw = ImageDraw.Draw(display_bg)
            bbox = d_draw.textbbox((0, 0), display_name, font=info_font)
            w = bbox[2] - bbox[0]
            d_draw.text(((card_width - 20 - w) // 2, 5), display_name, font=info_font, fill=(255, 255, 255))
            base.paste(display_bg, (card_x + 10, profile_y + img_size + 10), display_bg)

            safe_name = (actual_name[:20] + '..') if len(actual_name) > 20 else actual_name
            name_bg = Image.new('RGBA', (card_width - 10, 35), (40, 40, 40, 220))
            n_draw = ImageDraw.Draw(name_bg)
            bbox = n_draw.textbbox((0, 0), safe_name, font=name_font)
            w = bbox[2] - bbox[0]
            n_draw.text(((card_width - 10 - w) // 2, 5), safe_name, font=name_font, fill=(255, 255, 255))
            base.paste(name_bg, (card_x + 5, profile_y + img_size + 45), name_bg)

        # Draw avatars
        profile_size = 120
        draw_modern_profile(bg, user_img, user_card_x1, card_y, card_width, profile_size, "USER", user_name, False)
        draw_modern_profile(bg, bot_img, bot_card_x1, card_y, card_width, profile_size, "BOT", bot_name, True)

        # Service name
        service_bg = Image.new('RGBA', (width - 100, 60), (255, 215, 0, 200))
        s_draw = ImageDraw.Draw(service_bg)
        service_text = f"SERVICE: {service_name.upper()}"
        bbox = s_draw.textbbox((0, 0), service_text, font=service_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        s_draw.text(((width - 100 - w) // 2, (60 - h) // 2 - 5), service_text, font=service_font, fill=(10, 15, 30))
        bg.paste(service_bg, (50, card_y + card_height + 20), service_bg)

        # Footer
        footer_text = f"SocialHub Booster • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bbox = draw.textbbox((0, 0), footer_text, font=info_font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) // 2, height - 35), footer_text, font=info_font, fill=(200, 200, 200))

        # Safe filename generation
        safe_user = safe_filename(user_name)
        output_path = f"order_{safe_user}.png"
        
        bg.save(output_path, format='PNG', quality=95)
        
        # Safe logging
        log_message = safe_log_message(f"Notification image generated: {output_path}")
        logger.info(log_message)
        
        return output_path

    except Exception as e:
        error_msg = safe_log_message(f"Image generation error: {str(e)}")
        logger.error(error_msg)
        return generate_fallback_image(user_name, service_name)

def generate_fallback_image(user_name, service_name):
    """Simple fallback image"""
    try:
        width, height = 800, 400
        bg = Image.new("RGB", (width, height), (30, 30, 45))
        draw = ImageDraw.Draw(bg)
        title_font = ImageFont.load_default().font_variant(size=24)
        info_font = ImageFont.load_default().font_variant(size=16)
        draw.text((width//2, 100), "🛍️ ORDER NOTIFICATION", font=title_font, fill="white", anchor="mm")
        draw.text((width//2, 150), f"User: {user_name}", font=info_font, fill="yellow", anchor="mm")
        draw.text((width//2, 180), f"Service: {service_name}", font=info_font, fill="cyan", anchor="mm")
        draw.text((width//2, 250), "Powered by SocialHub Booster", font=info_font, fill="gray", anchor="mm")
        
        # Safe filename for fallback too
        safe_user = safe_filename(user_name)
        output_path = f"order_{safe_user}_fallback.png"
        bg.save(output_path, format='PNG')
        
        log_message = safe_log_message(f"Fallback image generated: {output_path}")
        logger.info(log_message)
        
        return output_path
    except Exception as e:
        error_msg = safe_log_message(f"Fallback image generation failed: {str(e)}")
        logger.error(error_msg)
        return None

def create_order_notification(bot, user_id, user_name, service_name, bot_name="SocialHub Booster"):
    """Main function to create order notification image"""
    try:
        # Get profile photos (with fallback to generated avatars)
        user_img = get_profile_photo(bot, user_id)
        bot_img = get_profile_photo(bot, bot.get_me().id)
        
        # Generate notification image
        image_path = generate_notification_image(
            user_img=user_img,
            bot_img=bot_img,
            user_name=user_name,
            bot_name=bot_name,
            service_name=service_name
        )
        
        return image_path
    except Exception as e:
        error_msg = safe_log_message(f"Error creating order notification: {str(e)}")
        logger.error(error_msg)
        return None

def cleanup_image(image_path):
    """Clean up generated image file"""
    try:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            logger.debug(f"Cleaned up image: {image_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up image {image_path}: {e}")
