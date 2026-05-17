import React, {useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import {ShieldCheck} from 'lucide-react-native';
import {Colors} from '../theme/Colors';

const SplashScreen = ({navigation}: any) => {
  useEffect(() => {
    setTimeout(() => {
      navigation.replace('Login');
    }, 3000);
  }, []);

  return (
    <LinearGradient colors={['#2196F3', '#0D47A1']} style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2196F3" />
      <View style={styles.content}>
        <Animatable.View
          animation="pulse"
          iterationCount="infinite"
          easing="ease-out"
          style={styles.logoContainer}>
          <ShieldCheck size={80} color="#FFFFFF" />
        </Animatable.View>
        <Animatable.Text animation="fadeInUp" delay={500} style={styles.title}>
          MedScan-AI
        </Animatable.Text>
        <Animatable.Text
          animation="fadeInUp"
          delay={800}
          style={styles.subtitle}>
          Scan. Verify. Stay Safe.
        </Animatable.Text>
      </View>
      <View style={styles.footer}>
        <ActivityIndicator color="#FFFFFF" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
  },
  logoContainer: {
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
  },
  title: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#FFFFFF',
    letterSpacing: 1,
  },
  subtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 10,
    letterSpacing: 0.5,
  },
  footer: {
    position: 'absolute',
    bottom: 50,
    alignItems: 'center',
  },
  loadingText: {
    color: '#FFFFFF',
    marginTop: 10,
    fontSize: 14,
    opacity: 0.7,
  },
});

export default SplashScreen;
