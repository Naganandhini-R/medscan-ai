export function isImageAcceptable(imageMeta: { sharpness: number; brightness: number }) {
    return (
        imageMeta.sharpness > 0.7 &&
        imageMeta.brightness > 0.4 &&
        imageMeta.brightness < 0.9
    );
}

