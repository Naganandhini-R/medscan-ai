import React from 'react';
import {
  Camera,
  useCameraDevice,
  useCameraFormat,
} from 'react-native-vision-camera';
import {StyleSheet} from 'react-native';
import {useIsFocused} from '@react-navigation/native';

export default function CameraView({
  cameraRef,
}: {
  cameraRef: React.RefObject<Camera>;
}) {
  const device = useCameraDevice('back');
  const isFocused = useIsFocused();

  // Select a standard format that supports photos
  const format = useCameraFormat(device, [{photoResolution: 'max'}, {fps: 30}]);

  if (!device) {
    return null;
  }

  return (
    <Camera
      ref={cameraRef}
      style={StyleSheet.absoluteFill}
      device={device}
      format={format}
      isActive={isFocused}
      photo={true}
      enableZoomGesture
    />
  );
}
