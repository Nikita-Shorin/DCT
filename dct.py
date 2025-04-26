import numpy as np
import cv2

class DCTSteganography:
    def __init__(self, block_size=8):
        self.block_size = block_size
        
    def embed_bit(self, block, bit, alpha=30):  # Увеличили силу встраивания
        dct_block = cv2.dct(np.float32(block))
        
        # Используем две позиции для надежности
        if bit == 1:
            dct_block[4,3] = abs(alpha)
            dct_block[3,4] = abs(alpha)
        else:
            dct_block[4,3] = -abs(alpha)
            dct_block[3,4] = -abs(alpha)
                
        block = cv2.idct(dct_block)
        return np.uint8(np.clip(block, 0, 255))

    def extract_bit(self, block):
        dct_block = cv2.dct(np.float32(block))
        # Используем среднее значение двух коэффициентов
        value = (dct_block[4,3] + dct_block[3,4]) / 2
        return 1 if value > 0 else 0

    def embed_message(self, image_path, message, output_path):
        img = cv2.imread(image_path, 0)
        if img is None:
            raise Exception("Не удалось прочитать изображение")
            
        height, width = img.shape
        print(f"Размеры изображения: {width}x{height}")
        
        message_bits = ''.join(format(ord(c), '08b') for c in message)
        message_length = len(message_bits)
        print(f"Длина сообщения в битах: {message_length}")
        print(f"Биты сообщения: {message_bits}")
        
        available_space = (height // self.block_size) * (width // self.block_size) - 32
        print(f"Доступное место в битах: {available_space}")
        
        if message_length > available_space:
            raise Exception("Сообщение слишком длинное для данного изображения")
        
        length_bits = format(message_length, '032b')
        print(f"Биты длины сообщения: {length_bits}")
        
        modified_img = img.copy()
        
        # Встраиваем биты длины сообщения
        for i in range(32):
            y = (i // (width // self.block_size)) * self.block_size
            x = (i % (width // self.block_size)) * self.block_size
            
            block = modified_img[y:y+self.block_size, x:x+self.block_size].copy()
            bit = int(length_bits[i])
            modified_block = self.embed_bit(block, bit)
            modified_img[y:y+self.block_size, x:x+self.block_size] = modified_block
            
        # Встраиваем биты сообщения
        for i in range(message_length):
            idx = i + 32
            y = (idx // (width // self.block_size)) * self.block_size
            x = (idx % (width // self.block_size)) * self.block_size
            
            block = modified_img[y:y+self.block_size, x:x+self.block_size].copy()
            bit = int(message_bits[i])
            modified_block = self.embed_bit(block, bit)
            modified_img[y:y+self.block_size, x:x+self.block_size] = modified_block
        
        cv2.imwrite(output_path, modified_img)
        print(f"Сообщение встроено и сохранено в {output_path}")

    def extract_message(self, image_path):
        img = cv2.imread(image_path, 0)
        if img is None:
            raise Exception("Не удалось прочитать изображение")
            
        height, width = img.shape
        print(f"Размеры изображения при извлечении: {width}x{height}")
        
        # Извлекаем биты длины сообщения
        length_bits = ''
        for i in range(32):
            y = (i // (width // self.block_size)) * self.block_size
            x = (i % (width // self.block_size)) * self.block_size
            
            block = img[y:y+self.block_size, x:x+self.block_size]
            bit = self.extract_bit(block)
            length_bits += str(bit)
        
        print(f"Извлеченные биты длины: {length_bits}")
        message_length = int(length_bits, 2)
        print(f"Извлеченная длина сообщения: {message_length} бит")
        
        # Извлекаем биты сообщения
        message_bits = ''
        for i in range(message_length):
            idx = i + 32
            y = (idx // (width // self.block_size)) * self.block_size
            x = (idx % (width // self.block_size)) * self.block_size
            
            block = img[y:y+self.block_size, x:x+self.block_size]
            bit = self.extract_bit(block)
            message_bits += str(bit)
        
        print(f"Извлеченные биты сообщения: {message_bits}")
        
        # Конвертируем биты в символы
        message = ''
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i+8]
            try:
                message += chr(int(byte, 2))
            except ValueError as e:
                print(f"Ошибка при конвертации байта {byte}: {e}")
                continue
            
        return message

# Основной код
if __name__ == "__main__":
    try:
        input_image = "input.jpg"
        stego = DCTSteganography()
        
        message = "Nikita Shorin"
        print(f"\nВстраивание сообщения: {message}")
        stego.embed_message(input_image, message, "output.png")
        
        print("\nИзвлечение сообщения:")
        extracted_message = stego.extract_message("output.png")
        print(f"Оригинальное сообщение: {message}")
        print(f"Извлеченное сообщение: {extracted_message}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
