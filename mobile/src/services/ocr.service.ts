import TextRecognition from 'react-native-mlkit-ocr';

export async function extractText(imagePath: string): Promise<string> {
    try {
        // Ensure path starts with file://
        const uri = imagePath.startsWith('file://') ? imagePath : `file://${imagePath}`;

        const result = await TextRecognition.detectFromUri(uri);

        // Combine all blocks into one string
        return result.map((block: any) => block.text).join('\n');
    } catch (error) {
        console.error('OCR error:', error);
        return '';
    }
}
