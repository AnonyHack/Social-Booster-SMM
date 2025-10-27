import os
import logging
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageFilter

# Setup logging
logger = logging.getLogger(__name__)

def get_profile_photo(bot, user_id):
    """Download and process profile photo"""
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
        logger.warning(f"Using default profile photo for {user_id}: {e}")
        # Create default gray circle (now matching the 500x500 size)
        img = Image.new("RGBA", (500, 500), (70, 70, 70, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, 500, 500), fill=(100, 100, 100, 255))
        return img

def generate_notification_image(user_img, bot_img, user_name, bot_name, service_name):
    """Generate a pro-quality notification image."""
    try:
        # Create base image with rich gradient background
        width, height = 800, 400
        bg = Image.new("RGB", (width, height), (30, 30, 45))
        gradient = Image.new("L", (1, height), color=0xFF)

        for y in range(height):
            gradient.putpixel((0, y), int(255 * (1 - y/height)))
        alpha_gradient = gradient.resize((width, height))
        black_img = Image.new("RGB", (width, height), color=(10, 10, 25))
        bg = Image.composite(bg, black_img, alpha_gradient)

        draw = ImageDraw.Draw(bg)

        # Fonts - added fallback for each font individually
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 40)
        except:
            title_font = ImageFont.load_default().font_variant(size=40)
            
        try:
            name_font = ImageFont.truetype("arialbd.ttf", 28)
        except:
            name_font = ImageFont.load_default().font_variant(size=28)
            
        try:
            service_font = ImageFont.truetype("arialbd.ttf", 24)
        except:
            service_font = ImageFont.load_default().font_variant(size=24)

        # Draw top title
        draw.text((width // 2, 40), "NEW ORDER NOTIFICATION", font=title_font,
                 fill="white", anchor="mm")

        # Helper to draw glowing circular image
        def draw_glowing_circle(base, img, pos, size, glow_color=(255, 215, 0)):
            glow = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            center = (glow.size[0] // 2, glow.size[1] // 2)

            for radius in range(size // 2 + 10, size // 2 + 20):
                glow_draw.ellipse([
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius
                ], fill=glow_color + (10,), outline=None)

            glow = glow.filter(ImageFilter.GaussianBlur(8))
            base.paste(glow, (pos[0] - 20, pos[1] - 20), glow)

            # Golden ring
            ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ring_draw = ImageDraw.Draw(ring)
            ring_draw.ellipse((0, 0, size - 1, size - 1), outline=(255, 215, 0), width=6)

            # Add mask to image (ensure we're working with RGBA)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img = img.resize((size, size))
            mask = Image.new('L', (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)

            base.paste(img, pos, img)
            base.paste(ring, pos, ring)

        # Paste profile images
        user_pos = (130, 120)
        bot_pos = (520, 120)
        draw_glowing_circle(bg, user_img, user_pos, 150)
        draw_glowing_circle(bg, bot_img, bot_pos, 150)

        # Draw usernames (with text length safety)
        max_name_length = 15
        safe_user_name = (user_name[:max_name_length] + '..') if len(user_name) > max_name_length else user_name
        safe_bot_name = (bot_name[:max_name_length] + '..') if len(bot_name) > max_name_length else bot_name
        
        draw.text((user_pos[0] + 75, 290), safe_user_name, font=name_font,
                 fill="white", anchor="ma")
        draw.text((bot_pos[0] + 75, 290), safe_bot_name, font=name_font,
                 fill="white", anchor="ma")

        # Draw service name in the middle (with safety check)
        max_service_length = 30
        safe_service_name = (service_name[:max_service_length] + '..') if len(service_name) > max_service_length else service_name
        draw.text((width // 2, 330), f"Service: {safe_service_name}", font=service_font,
                 fill=(255, 215, 0), anchor="ma")

        # Bottom banner
        draw.rectangle([0, 370, width, 400], fill=(255, 215, 0))
        draw.text((width // 2, 385), "Powered by SocialHub Booster", font=name_font,
                 fill=(30, 30, 30), anchor="mm")

        output_path = f"order_{user_name[:50]}.png"  # Limit filename length
        bg.save(output_path, quality=95)
        logger.info(f"Notification image generated: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

def create_order_notification(bot, user_id, user_name, service_name, bot_name="SocialHub Booster"):
    """Main function to create order notification image"""
    try:
        # Get profile photos
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
        logger.error(f"Error creating order notification: {e}")
        return None

def cleanup_image(image_path):
    """Clean up generated image file"""
    try:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            logger.debug(f"Cleaned up image: {image_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up image {image_path}: {e}")