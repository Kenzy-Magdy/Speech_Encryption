import pyaudio #libary hnst5dmha fe enna na5od elspeech mn mic 
import wave #hnst5dmha enna n3ml save lel audio as a wave file 
from Crypto.Cipher import AES, PKCS1_OAEP #da eli hydena access lel aes
from Crypto.PublicKey import RSA # nfs eli fo2 bs le rsa 
from Crypto.Random import get_random_bytes #hysm7lna n generate keys 
from Crypto.Util.Padding import pad, unpad #3shan a3rf a insert fel data w a3mlha elimination

# Constants
CHUNK_SIZE = 1024 #in bits 
FORMAT = pyaudio.paInt16 
CHANNELS = 1 #el mic only 
RATE = 44100 #3dd el samples collected per sec 
RECORD_SECONDS = 10 #modet el recording (momken nzwdha aw nn2sha )
AES_KEY_SIZE = 32 #bytes =256bit
RSA_KEY_SIZE = 2048 #bit 

# el key bta3 el rsa 
key = RSA.generate(RSA_KEY_SIZE)
public_key = key.publickey()

# hnsm3 el speech be mic 
def record_speech(output_file):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    print("Recording speech...")
    frames = []
    for _ in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)): # el range aw el wa2t eli h2ra feh el sot b3d keda ay speech tb2a neglegable 
        data = stream.read(CHUNK_SIZE)
        frames.append(data) #hsgl el speech 3la shakl frames 

    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # hn3ml save lel audio 3la shakl wave file 
    wave_file = wave.open(output_file, 'wb')
    
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

# nbd2 el encryption lel speech using aes 
def encrypt_speech(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_CBC) #cipher block chaining 
    file_out = open(output_file, "wb")

    # vector hn7tago ba3deen fel decryption 
    file_out.write(cipher.iv)

    # n3ml encryption lel data bta3t el speech
    with open(input_file, 'rb') as file_in:
        while True:
            chunk = file_in.read(16)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0: 
                chunk = pad(chunk, 16) 
            ciphertext = cipher.encrypt(chunk)
            file_out.write(ciphertext) 

    file_out.close()

# n3ml encrypt lel key bta3 el aes using rsa 
def encrypt_aes_key(aes_key, rsa_public_key):
    cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    return encrypted_aes_key  #keda el7aga htro7 lel reciever metshfra 

# decrypt el key bta3 el aes using rsa 
def decrypt_aes_key(encrypted_aes_key, rsa_private_key):
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)
    return aes_key #el mrady elkey hyro7 mesh metshfr 

# wb3d kda nfok elspeech using el key 
def decrypt_speech(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=key[:16])
    file_out = open(output_file, "wb")

    with open(input_file, 'rb') as file_in:
        # hn2ra el vector eli 3mlnalo intialize fo2 
        iv = file_in.read(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt el data bta3t el speech 
        decrypted_data = b''
        while True:
            chunk = file_in.read(16)
            if len(chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(chunk)
            decrypted_data += decrypted_chunk

        # Remove the padding
        decrypted_data = unpad(decrypted_data, 16)

        # Write the decrypted data to the output file
        file_out.write(decrypted_data)

    file_out.close()

# da el code yo3tbr b3d m3rfna el functions fo2 
aes_key = get_random_bytes(AES_KEY_SIZE)

# hn3ml record we encryption lel speech 
record_speech("speech.wav")
encrypt_speech("speech.wav", "encrypted_speech.bin", aes_key)

#n3ml encrypt lel key using rsa key (public)
encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

# n3ml decrypt lel key using rsa (private )
decrypted_aes_key = decrypt_aes_key(encrypted_aes_key, key)

# n generate speech b3d m5lsna el project 
decrypt_speech("encrypted_speech.bin", "decrypted_speech.wav", decrypted_aes_key)