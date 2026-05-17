import React, { useRef, useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  Text,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Dimensions,
  Linking,
} from 'react-native';
import { Camera } from 'react-native-vision-camera';
import { ArrowLeft, Zap, Info, Camera as CameraIcon, Image as ImageIcon } from 'lucide-react-native';
import { launchImageLibrary } from 'react-native-image-picker';
import { useIsFocused, useFocusEffect } from '@react-navigation/native';
import * as Animatable from 'react-native-animatable';
import CameraView from '../components/CameraView';
import { Colors } from '../theme/Colors';

const { width, height } = Dimensions.get('window');
const angles = ['Front', 'Back', 'Composition'];

import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Scan'>;

export default function ScanScreen({ navigation }: Props) {
  const cameraRef = useRef<Camera>(null);
  const [step, setStep] = useState(0);
  const [images, setImages] = useState<any>({});
  const [flash, setFlash] = useState<'off' | 'on'>('off');
  const [hasPermission, setHasPermission] = useState<boolean>(false);

  const isFocused = useIsFocused();

  useFocusEffect(
    React.useCallback(() => {
      setStep(0);
      setImages({});
      setCameraReady(false);
    }, []),
  );

  useEffect(() => {
    checkPermission();
  }, []);

  const checkPermission = async () => {
    const status = await Camera.getCameraPermissionStatus();
    if (status === 'granted') {
      setHasPermission(true);
    } else if (status === 'not-determined') {
      const request = await Camera.requestCameraPermission();
      setHasPermission(request === 'granted');
    } else {
      Alert.alert(
        'Camera Permission',
        'Camera access is denied. Please enable it in settings to continue.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Open Settings', onPress: () => Linking.openSettings() },
        ],
      );
    }
  };

  const [cameraReady, setCameraReady] = useState(false);

  useEffect(() => {
    if (hasPermission) {
      // Give hardware 1s to stabilize
      const timer = setTimeout(() => setCameraReady(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [hasPermission]);

  const capture = async () => {
    if (!cameraReady || !cameraRef.current) return;
    try {
      const photo = await cameraRef.current.takePhoto({
        flash: flash,
      });
      const angle = angles[step].toLowerCase();
      const newImages = { ...images, [angle]: photo?.path || '' };
      setImages(newImages);

      if (step < 2) {
        setStep(step + 1);
      } else {
        navigation.navigate('Review', { images: newImages });
      }
    } catch (e) {
      console.error('Capture Error:', e);
      Alert.alert('Camera error', 'Failed to capture image. Please try again.');
    }
  };

  const pickImage = async () => {
    try {
      const result = await launchImageLibrary({
        mediaType: 'photo',
        quality: 0.8,
        includeExtra: true,
      });

      if (result.didCancel) return;
      if (result.errorCode) {
        Alert.alert('Selection Error', result.errorMessage || 'Failed to pick image');
        return;
      }

      if (result.assets && result.assets.length > 0 && result.assets[0].uri) {
        const pickedImage = result.assets[0].uri;
        // Move straight to review with the picked image as front
        navigation.navigate('Review', {
          images: { front: pickedImage }
        });
      }
    } catch (error) {
      console.error('Pick Image Error:', error);
      Alert.alert('Error', 'An unexpected error occurred while picking the image.');
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar
        barStyle="light-content"
        translucent
        backgroundColor="transparent"
      />

      <View style={styles.cameraWrapper}>
        {hasPermission ? (
          <CameraView cameraRef={cameraRef} />
        ) : (
          <View style={styles.noPermissionContainer}>
            <CameraIcon color="rgba(255,255,255,0.3)" size={64} />
            <Text style={styles.noPermissionText}>
              Waiting for Camera Permission...
            </Text>
            <TouchableOpacity onPress={checkPermission} style={styles.retryBtn}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Futuristic Holographic Overlay */}
      <View style={styles.hudOverlay}>
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.header}>
            <TouchableOpacity
              onPress={() => navigation.goBack()}
              style={styles.glassBtn}>
              <ArrowLeft color="#FFF" size={24} />
            </TouchableOpacity>

            <View style={styles.aiStatus}>
              <View style={styles.pulseContainer}>
                <Animatable.View
                  animation={{
                    0: { scaleX: 1, scaleY: 1, opacity: 0.8 },
                    1: { scaleX: 2, scaleY: 2, opacity: 0 }
                  }}
                  duration={2000}
                  iterationCount="infinite"
                  style={styles.pulseDot}
                />
                <View style={styles.liveDot} />
              </View>
              <Text style={styles.statusText}>AI LIVE SCAN</Text>
            </View>

            <TouchableOpacity
              onPress={() => setFlash(flash === 'on' ? 'off' : 'on')}
              style={styles.glassBtn}>
              <Zap color={flash === 'on' ? '#fbbf24' : '#FFF'} size={24} />
            </TouchableOpacity>
          </View>

          <View style={styles.scanningZone}>
            {/* Precision Target Frame */}
            <View style={styles.apertureBox}>
              <View style={[styles.cornerBox, styles.tl]} />
              <View style={[styles.cornerBox, styles.tr]} />
              <View style={[styles.cornerBox, styles.bl]} />
              <View style={[styles.cornerBox, styles.br]} />

              {/* Advanced Scanning Beam */}
              <Animatable.View
                animation={{
                  0: { translateY: -100, opacity: 0 },
                  0.5: { opacity: 1 },
                  1: { translateY: 280, opacity: 0 },
                }}
                duration={2500}
                iterationCount="infinite"
                style={styles.scannerBeam}
              />

              {/* Center Aim */}
              <View style={styles.centerAim}>
                <View style={styles.aimCrossH} />
                <View style={styles.aimCrossV} />
              </View>
            </View>

            <Animatable.View animation="fadeIn" style={styles.compactInstruction}>
              <Text style={styles.compactText}>
                Step {step + 1}: Scan <Text style={{ color: Colors.primary }}>{angles[step]}</Text> Side
              </Text>
            </Animatable.View>
          </View>

          <View style={styles.controlsSection}>
            <View style={styles.techBar}>
              <View style={[styles.barSegment, step >= 1 && styles.activeSegment]} />
              <View style={[styles.barSegment, step >= 2 && styles.activeSegment]} />
              <View style={[styles.barSegment, step >= 3 && styles.activeSegment]} />
            </View>

            <View style={styles.mainControls}>
              <TouchableOpacity onPress={pickImage} style={styles.sideControl}>
                <ImageIcon color="rgba(255,255,255,0.8)" size={24} />
                <Text style={styles.sideText}>Gallery</Text>
              </TouchableOpacity>

              <TouchableOpacity
                activeOpacity={0.8}
                onPress={capture}
                style={styles.captureRing}
              >
                <View style={styles.captureCore}>
                  <View style={styles.captureInnerCircle} />
                </View>
              </TouchableOpacity>

              <View style={styles.sideControl}>
                <View style={styles.stepProgressContainer}>
                  <Text style={styles.progressText}>{Math.round(((step) / 3) * 100)}%</Text>
                </View>
                <Text style={styles.sideText}>Ready</Text>
              </View>
            </View>

            <View style={styles.legalInfo}>
              <Info size={14} color="#94a3b8" />
              <Text style={styles.legalText}>
                AI is analyzing pixel-level forensic data for authentication
              </Text>
            </View>
          </View>
        </SafeAreaView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  cameraWrapper: { ...StyleSheet.absoluteFillObject },
  hudOverlay: { ...StyleSheet.absoluteFillObject },
  safeArea: { flex: 1 },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 15,
  },
  glassBtn: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  aiStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 30,
    gap: 10,
    borderWidth: 1,
    borderColor: Colors.primary,
  },
  pulseContainer: {
    width: 12,
    height: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Colors.primary,
    position: 'absolute',
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.primary,
  },
  statusText: {
    color: Colors.primary,
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 1.5,
  },

  scanningZone: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  apertureBox: {
    width: width * 0.9,
    height: 320,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.15)',
    borderRadius: 30,
    backgroundColor: 'rgba(0,0,0,0.2)',
    position: 'relative',
  },
  cornerBox: {
    position: 'absolute',
    width: 30,
    height: 30,
    borderColor: Colors.primary,
    borderWidth: 3,
  },
  tl: { top: -2, left: -2, borderBottomWidth: 0, borderRightWidth: 0, borderTopLeftRadius: 20 },
  tr: { top: -2, right: -2, borderBottomWidth: 0, borderLeftWidth: 0, borderTopRightRadius: 20 },
  bl: { bottom: -2, left: -2, borderTopWidth: 0, borderRightWidth: 0, borderBottomLeftRadius: 20 },
  br: { bottom: -2, right: -2, borderTopWidth: 0, borderLeftWidth: 0, borderBottomRightRadius: 20 },

  scannerBeam: {
    width: '100%',
    height: 60,
    backgroundColor: 'rgba(33, 150, 243, 0.2)',
    borderBottomWidth: 2,
    borderBottomColor: Colors.primary,
  },
  centerAim: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    opacity: 0.3,
  },
  aimCrossH: { width: 40, height: 1, backgroundColor: '#FFF' },
  aimCrossV: { height: 40, width: 1, backgroundColor: '#FFF', position: 'absolute' },

  compactInstruction: {
    marginTop: 60,
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 30,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  compactText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 0.5,
  },

  controlsSection: {
    paddingBottom: 40,
    paddingHorizontal: 30,
  },
  techBar: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 30,
    paddingHorizontal: 50,
  },
  barSegment: {
    flex: 1,
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 2,
  },
  activeSegment: {
    backgroundColor: Colors.primary,
  },

  mainControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  sideControl: {
    alignItems: 'center',
    width: 60,
  },
  sideText: {
    color: '#94a3b8',
    fontSize: 10,
    marginTop: 8,
    fontWeight: 'bold',
  },
  captureRing: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: 'rgba(255,255,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureCore: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 15,
    elevation: 20,
  },
  captureInnerCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  stepProgressContainer: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  progressText: { color: Colors.primary, fontSize: 12, fontWeight: 'bold' },

  noPermissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    gap: 20,
  },
  noPermissionText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  retryBtn: {
    paddingHorizontal: 25,
    paddingVertical: 12,
    backgroundColor: Colors.primary,
    borderRadius: 15,
  },
  retryText: { color: '#FFF', fontWeight: 'bold' },

  legalInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  legalText: {
    color: '#64748b',
    fontSize: 11,
    textAlign: 'center',
  },
});
