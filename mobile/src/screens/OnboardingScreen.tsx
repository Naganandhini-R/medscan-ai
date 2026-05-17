import React, {useState, useRef} from 'react';
// Triggering metro refresh
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  Dimensions,
  TouchableOpacity,
  Image,
  StatusBar,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import {ChevronRight, ArrowRight} from 'lucide-react-native';
import {Colors} from '../theme/Colors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {finishOnboarding as apiFinishOnboarding} from '../services/api.service';

const {width, height} = Dimensions.get('window');

const slides = [
  {
    id: '1',
    title: 'Scan Your Medicine',
    subtitle:
      'Our advanced AI analyzes every detail of your medicine packaging to ensure its authenticity instantly.',
    image: require('../assets/onboarding1.png'),
    primaryColor: '#2196F3',
  },
  {
    id: '2',
    title: 'AI Checks Authenticity',
    subtitle:
      'We verify batch numbers, barcodes, and manufacturing details against global pharmaceutical databases.',
    image: require('../assets/onboarding2.png'),
    primaryColor: '#0D47A1',
  },
  {
    id: '3',
    title: 'Safe for Consumption',
    subtitle:
      'Get a clear safety report, expiry alerts, and detailed dosage info to keep you and your family safe.',
    image: require('../assets/onboarding3.png'),
    primaryColor: '#10B981',
  },
];

const OnboardingScreen = ({navigation}: any) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const handleNext = async () => {
    if (currentIndex < slides.length - 1) {
      flatListRef.current?.scrollToIndex({index: currentIndex + 1});
      setCurrentIndex(currentIndex + 1);
    } else {
      await finishOnboarding();
    }
  };

  const handleSkip = async () => {
    await finishOnboarding();
  };

  const finishOnboarding = async () => {
    try {
      const userStr = await AsyncStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        await apiFinishOnboarding(user.id);
        // Update local user object
        user.has_boarded = true;
        await AsyncStorage.setItem('user', JSON.stringify(user));
      }
      await AsyncStorage.setItem('hasBoarded', 'true');
      navigation.replace('Home');
    } catch (e) {
      console.error(e);
      navigation.replace('Home');
    }
  };

  const renderItem = ({item}: any) => (
    <View style={styles.slide}>
      <Animatable.View
        animation="fadeIn"
        duration={1000}
        style={styles.imageContainer}>
        {item.image ? (
          <Image
            source={item.image}
            style={styles.image}
            resizeMode="contain"
          />
        ) : (
          <View
            style={[
              styles.image,
              {backgroundColor: item.primaryColor + '20', borderRadius: 20},
            ]}
          />
        )}
      </Animatable.View>

      <View style={styles.contentContainer}>
        <Animatable.Text animation="fadeInUp" delay={200} style={styles.title}>
          {item.title}
        </Animatable.Text>
        <Animatable.Text
          animation="fadeInUp"
          delay={400}
          style={styles.subtitle}>
          {item.subtitle}
        </Animatable.Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFF" />
      <View style={styles.topRow}>
        <TouchableOpacity onPress={handleSkip}>
          <Text style={styles.skipText}>Skip</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={slides}
        renderItem={renderItem}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={e => {
          const index = Math.round(e.nativeEvent.contentOffset.x / width);
          setCurrentIndex(index);
        }}
        keyExtractor={item => item.id}
      />

      <View style={styles.footer}>
        <View style={styles.pagination}>
          {slides.map((_, index) => (
            <View
              key={index}
              style={[styles.dot, currentIndex === index && styles.activeDot]}
            />
          ))}
        </View>

        <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
          <LinearGradient
            colors={['#2196F3', '#0D47A1']}
            style={styles.btnGradient}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 0}}>
            <Text style={styles.btnText}>
              {currentIndex === slides.length - 1 ? 'Get Started' : 'Next'}
            </Text>
            <ArrowRight color="#FFF" size={20} style={{marginLeft: 10}} />
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#FFF'},
  topRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    paddingHorizontal: 25,
    paddingTop: 10,
  },
  skipText: {
    fontSize: 16,
    color: Colors.textSub,
    fontWeight: '600',
  },
  slide: {
    width,
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  imageContainer: {
    width: width * 0.8,
    height: height * 0.4,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 40,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  contentContainer: {
    alignItems: 'center',
    marginTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.textHeader,
    textAlign: 'center',
    marginBottom: 15,
  },
  subtitle: {
    fontSize: 16,
    color: Colors.textSub,
    textAlign: 'center',
    lineHeight: 24,
  },
  footer: {
    paddingHorizontal: 40,
    paddingBottom: 40,
    alignItems: 'center',
  },
  pagination: {
    flexDirection: 'row',
    marginBottom: 40,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#E2E8F0',
    marginHorizontal: 5,
  },
  activeDot: {
    backgroundColor: Colors.primary,
    width: 25,
  },
  nextButton: {
    width: '100%',
    height: 56,
    borderRadius: 28,
    overflow: 'hidden',
    elevation: 5,
    shadowColor: Colors.primary,
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  btnGradient: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default OnboardingScreen;
