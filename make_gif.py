from PIL import Image, ImageSequence

# Load the spritesheet from the uploaded file
spritesheet_path = "/Users/mac/Desktop/Loss_function/image_folder/DALL·E 2023-12-12 16.39.53 - Create a sprite sheet featuring the letter 'D' with a simple, bold, and clear design, bouncing within each frame. The sprite sheet should consist of 1.png"
spritesheet = Image.open(spritesheet_path)

# Calculate the size of each sprite
sprite_width = spritesheet.width // 3
sprite_height = spritesheet.height // 3

# List to hold each sprite image
sprites = []

# Extract sprites from the spritesheet
for row in range(4):
    for col in range(4):
        # Define the area to crop
        left = col * sprite_width
        upper = row * sprite_height
        right = (col + 1) * sprite_width
        lower = (row + 1) * sprite_height

        # Crop the sprite and append to the list
        sprite = spritesheet.crop((left, upper, right, lower))
        sprites.append(sprite)

# Create the GIF
output_gif_path = './gif_videos_folder/letter_d_animation.gif'
sprites[0].save(
    output_gif_path,
    save_all=True,
    append_images=sprites[1:],
    optimize=False,
    duration=150, # duration for each frame in milliseconds
    loop=0 # loop forever
)

output_gif_path
