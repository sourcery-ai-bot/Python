import os
import sys

from . import rsa_key_generator as rkg

DEFAULT_BLOCK_SIZE = 128
BYTE_SIZE = 256


def main():
    filename = "encrypted_file.txt"
    response = input(r"Encrypt\Decrypt [e\d]: ")

    if response.lower().startswith("e"):
        mode = "encrypt"
    elif response.lower().startswith("d"):
        mode = "decrypt"

    if mode == "encrypt":
        if not os.path.exists("rsa_pubkey.txt"):
            rkg.makeKeyFiles("rsa", 1024)

        message = input("\nEnter message: ")
        pubKeyFilename = "rsa_pubkey.txt"
        print("Encrypting and writing to %s..." % (filename))
        encryptedText = encryptAndWriteToFile(filename, pubKeyFilename, message)

        print("\nEncrypted text:")
        print(encryptedText)

    elif mode == "decrypt":
        privKeyFilename = "rsa_privkey.txt"
        print("Reading from %s and decrypting..." % (filename))
        decryptedText = readFromFileAndDecrypt(filename, privKeyFilename)
        print("writing decryption to rsa_decryption.txt...")
        with open("rsa_decryption.txt", "w") as dec:
            dec.write(decryptedText)

        print("\nDecryption:")
        print(decryptedText)


def getBlocksFromText(message: int, blockSize: int = DEFAULT_BLOCK_SIZE) -> [int]:
    messageBytes = message.encode("ascii")

    blockInts = []
    for blockStart in range(0, len(messageBytes), blockSize):
        blockInt = sum(
            messageBytes[i] * (BYTE_SIZE ** (i % blockSize))
            for i in range(
                blockStart, min(blockStart + blockSize, len(messageBytes))
            )
        )

        blockInts.append(blockInt)
    return blockInts


def getTextFromBlocks(
    blockInts: [int], messageLength: int, blockSize: int = DEFAULT_BLOCK_SIZE
) -> str:
    message = []
    for blockInt in blockInts:
        blockMessage = []
        for i in range(blockSize - 1, -1, -1):
            if len(message) + i < messageLength:
                asciiNumber = blockInt // (BYTE_SIZE ** i)
                blockInt = blockInt % (BYTE_SIZE ** i)
                blockMessage.insert(0, chr(asciiNumber))
        message.extend(blockMessage)
    return "".join(message)


def encryptMessage(
    message: str, key: (int, int), blockSize: int = DEFAULT_BLOCK_SIZE
) -> [int]:
    n, e = key

    return [pow(block, e, n) for block in getBlocksFromText(message, blockSize)]


def decryptMessage(
    encryptedBlocks: [int],
    messageLength: int,
    key: (int, int),
    blockSize: int = DEFAULT_BLOCK_SIZE,
) -> str:
    n, d = key
    decryptedBlocks = [pow(block, d, n) for block in encryptedBlocks]
    return getTextFromBlocks(decryptedBlocks, messageLength, blockSize)


def readKeyFile(keyFilename: str) -> (int, int, int):
    with open(keyFilename) as fo:
        content = fo.read()
    keySize, n, EorD = content.split(",")
    return (int(keySize), int(n), int(EorD))


def encryptAndWriteToFile(
    messageFilename: str,
    keyFilename: str,
    message: str,
    blockSize: int = DEFAULT_BLOCK_SIZE,
) -> str:
    keySize, n, e = readKeyFile(keyFilename)
    if keySize < blockSize * 8:
        sys.exit(
            "ERROR: Block size is %s bits and key size is %s bits. The RSA cipher "
            "requires the block size to be equal to or greater than the key size. "
            "Either decrease the block size or use different keys."
            % (blockSize * 8, keySize)
        )

    encryptedBlocks = encryptMessage(message, (n, e), blockSize)

    for i in range(len(encryptedBlocks)):
        encryptedBlocks[i] = str(encryptedBlocks[i])
    encryptedContent = ",".join(encryptedBlocks)
    encryptedContent = "{}_{}_{}".format(len(message), blockSize, encryptedContent)
    with open(messageFilename, "w") as fo:
        fo.write(encryptedContent)
    return encryptedContent


def readFromFileAndDecrypt(messageFilename: str, keyFilename: str) -> str:
    keySize, n, d = readKeyFile(keyFilename)
    with open(messageFilename) as fo:
        content = fo.read()
    messageLength, blockSize, encryptedMessage = content.split("_")
    messageLength = int(messageLength)
    blockSize = int(blockSize)

    if keySize < blockSize * 8:
        sys.exit(
            "ERROR: Block size is %s bits and key size is %s bits. The RSA cipher "
            "requires the block size to be equal to or greater than the key size. "
            "Did you specify the correct key file and encrypted file?"
            % (blockSize * 8, keySize)
        )

    encryptedBlocks = [int(block) for block in encryptedMessage.split(",")]
    return decryptMessage(encryptedBlocks, messageLength, (n, d), blockSize)


if __name__ == "__main__":
    main()
