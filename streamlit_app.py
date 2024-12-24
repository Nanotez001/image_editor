import streamlit as st
from PIL import Image
import pandas as pd

class ImageAnalyzer:
    def __init__(self, image_path, tolerance=10):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGB")  # Convert image to RGB mode
        self.pixels = self.image.load()
        self.width, self.height = self.image.size
        self.tolerance = tolerance  # Set the tolerance

    def is_almost_white(self, pixel):
        return all(255 - value <= self.tolerance for value in pixel)

    def find_leftmost_nonwhite(self):
        for x in range(self.width):
            for y in range(self.height):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return x
        return -1

    def find_uppermost_nonwhite(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return y
        return -1

    def find_rightmost_nonwhite(self):
        for x in range(self.width - 1, -1, -1):
            for y in range(self.height):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return x
        return -1

    def find_downmost_nonwhite(self):
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return y
        return -1


    def paste_image(self, overlay_image_path, coordinates=(0, 0)):
        overlay_image = Image.open(overlay_image_path).convert("RGBA")
        if coordinates[0] + overlay_image.width > self.image.width or coordinates[1] + overlay_image.height > self.image.height:
            raise ValueError("Overlay image goes beyond the base image dimensions.")
        self.image.paste(overlay_image, coordinates, overlay_image)
        return self.image

    def layout_images(self, image_paths, layout="horizontal"):
        images = [Image.open(path).convert("RGB") for path in image_paths]
        widths, heights = zip(*(img.size for img in images))

        if layout == "horizontal":
            total_width = sum(widths)
            max_height = max(heights)
            new_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))
            x_offset = 0
            for img in images:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.width
        elif layout == "vertical":
            total_height = sum(heights)
            max_width = max(widths)
            new_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))
            y_offset = 0
            for img in images:
                new_img.paste(img, (0, y_offset))
                y_offset += img.height
        else:
            raise ValueError("Invalid layout type. Choose 'horizontal' or 'vertical'.")

        return new_img

    def merge_images(self, image1_path, image2_path, alpha=0.5):
        img1 = Image.open(image1_path).convert("RGBA")
        img2 = Image.open(image2_path).convert("RGBA")
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        return Image.blend(img1, img2, alpha)

    def crop(self, left, upper, right, lower):
        # Validate crop dimensions
        if left < 0 or upper < 0 or right > self.width or lower > self.height:
            raise ValueError("Crop coordinates are out of image bounds.")
        if left >= right or upper >= lower:
            raise ValueError("Invalid crop dimensions. Ensure left < right and upper < lower.")
        
        # Perform the cropping
        cropped_image = self.image.crop((left, upper, right, lower))
        return cropped_image
    def resize_with_aspect_ratio(self, new_width=None, new_height=None):
        if new_width is None and new_height is None:
            raise ValueError("At least one of new_width or new_height must be specified.")

        # Calculate the aspect ratio of the image
        aspect_ratio = self.width / self.height

        if new_width is not None:
            # Calculate new height while maintaining aspect ratio
            new_height = int(new_width / aspect_ratio)
        elif new_height is not None:
            # Calculate new width while maintaining aspect ratio
            new_width = int(new_height * aspect_ratio)

        # Resize the image
        resized_image = self.image.resize((new_width, new_height))
        return resized_image

# # Example Usage
# if __name__ == "__main__":
#     # image_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/65qned80tsa.jpeg"
#     image_path = "D:/Nano_HomeWork/Pic/เครื่องซักผ้า/LG/FV1412S2B/FV1412S2B-01.jpg"
#     background_525x338 = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Temp_525x338.jpg"  # Replace with your image file path
#     background_size=[525,338]
#     analyzer = ImageAnalyzer(image_path)

    

#     leftmost_x = analyzer.find_leftmost_nonwhite()
#     uppermost_y = analyzer.find_uppermost_nonwhite()
#     rightmost_x = analyzer.find_rightmost_nonwhite()
#     downmost_y = analyzer.find_downmost_nonwhite()
#     # print("SIZE",analyzer.image.size)

#     cropped_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Cropped_Test.jpg"
#     resized_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Resized_Test.jpg"
#     background_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Temp_525x338.jpg"

#     # Crop the image and save it
#     cropped_image = analyzer.crop(leftmost_x, uppermost_y, rightmost_x, downmost_y)
#     cropped_image.save(cropped_path)

#     # Resize the cropped image and save it
#     resized_image = ImageAnalyzer(cropped_path).resize_with_aspect_ratio(new_height=254)
#     resized_image.save(resized_path)

#     # Overlay the resized image onto the background
#     background = ImageAnalyzer(background_path)
#     result = background.paste_image(resized_path, coordinates=((background_size[0]-resized_image.width)//2,42))

#     result.show()
#     result.save("C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Result_Test.jpg")
pp_df=pd.read_csv("https://raw.githubusercontent.com/Nanotez001/image_editor/refs/heads/main/Platfrom_Product.csv")

# ====================================
def main():
    st.title("IMAGE EDITOR")

    # Sidebar components
    st.sidebar.title("Select Options")

    # Sidebar widgets
    platfrom = st.sidebar.selectbox("Platfrom:", ["LD", "JJT"])
    type_product = st.sidebar.selectbox("Type:", ["TV", "ตู้เย็น","ไมโครเวฟ"])
    buffer=pp_df.loc[platfrom,type_product]

    uploaded_file = st.file_uploader("Upload JPG Files",type=["jpg", "jpeg"],accept_multiple_files=True)

    col1, col2 = st.columns(2)
    # Display the images side by side
    old_imge_url= "https://via.placeholder.com/300x200.png?text=Image+1"
    new_imge_url="https://via.placeholder.com/300x200.png?text=Image+2"

    with col1:
        st.image(old_imge_url, caption="Before", use_container_width=True)

    with col2:
        st.image(new_imge_url, caption="After", use_container_width=True)



# Run the app
if __name__ == "__main__":
    main()