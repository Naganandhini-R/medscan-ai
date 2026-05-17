import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StatusBar,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {
  Mail,
  Lock,
  User,
  Phone,
  ArrowLeft,
  Eye,
  EyeOff,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import {signup, login} from '../services/api.service';
import {Colors} from '../theme/Colors';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SignupScreen = ({navigation}: any) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!name || !email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      // 1. Create Account
      await signup(name, email, password);

      // 2. Auto Login
      const data = await login(email, password);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));

      Alert.alert('Success', 'Account created successfully!', [
        {
          text: 'OK',
          onPress: () => {
            if (data.user.has_boarded) {
              navigation.reset({
                index: 0,
                routes: [{name: 'Home'}],
              });
            } else {
              navigation.replace('Onboarding');
            }
          },
        },
      ]);
    } catch (e: any) {
      Alert.alert(
        'Error',
        e.message || 'Registration failed. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8FAFC" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{flex: 1}}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={styles.backBtn}>
            <ArrowLeft size={24} color={Colors.textHeader} />
          </TouchableOpacity>

          <Animatable.View animation="fadeInDown" style={styles.header}>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>
              Join MedScan-AI and start verifying your medicines today.
            </Text>
          </Animatable.View>

          <Animatable.View
            animation="fadeInUp"
            delay={300}
            style={styles.formContainer}>
            <View style={styles.inputGroup}>
              <View style={styles.inputWrapper}>
                <User
                  size={20}
                  color={Colors.textSub}
                  style={styles.inputIcon}
                />
                <TextInput
                  placeholder="Full Name"
                  value={name}
                  onChangeText={setName}
                  style={styles.input}
                  placeholderTextColor={Colors.textSub}
                />
              </View>

              <View style={styles.inputWrapper}>
                <Mail
                  size={20}
                  color={Colors.textSub}
                  style={styles.inputIcon}
                />
                <TextInput
                  placeholder="Email Address"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  style={styles.input}
                  placeholderTextColor={Colors.textSub}
                />
              </View>

              <View style={styles.inputWrapper}>
                <Lock
                  size={20}
                  color={Colors.textSub}
                  style={styles.inputIcon}
                />
                <TextInput
                  placeholder="Password"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                  style={styles.input}
                  placeholderTextColor={Colors.textSub}
                />
                <TouchableOpacity
                  onPress={() => setShowPassword(!showPassword)}
                  style={styles.eyeIcon}>
                  {showPassword ? (
                    <EyeOff size={20} color={Colors.textSub} />
                  ) : (
                    <Eye size={20} color={Colors.textSub} />
                  )}
                </TouchableOpacity>
              </View>
            </View>

            <TouchableOpacity
              onPress={handleSignup}
              style={[styles.signUpButton, loading && {opacity: 0.7}]}
              disabled={loading}>
              <LinearGradient
                colors={['#2196F3', '#42A5F5']}
                start={{x: 0, y: 0}}
                end={{x: 1, y: 0}}
                style={styles.buttonGradient}>
                {loading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <Text style={styles.buttonText}>Create Account</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <View style={styles.footer}>
              <Text style={styles.footerText}>Already have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                <Text style={styles.signInText}>Sign In</Text>
              </TouchableOpacity>
            </View>
          </Animatable.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#F8FAFC'},
  scrollContent: {padding: 24, flexGrow: 1},
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F1F5F9',
    marginBottom: 20,
  },
  header: {marginBottom: 40},
  title: {fontSize: 28, fontWeight: 'bold', color: Colors.textHeader},
  subtitle: {fontSize: 16, color: Colors.textSub, marginTop: 8},
  formContainer: {flex: 1},
  inputGroup: {gap: 16},
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 56,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  inputIcon: {marginRight: 12},
  input: {flex: 1, fontSize: 16, color: Colors.textHeader, height: '100%'},
  eyeIcon: {padding: 4},
  signUpButton: {
    marginTop: 30,
    height: 56,
    borderRadius: 12,
    overflow: 'hidden',
  },
  buttonGradient: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  buttonText: {color: '#FFF', fontSize: 18, fontWeight: 'bold'},
  footer: {flexDirection: 'row', justifyContent: 'center', marginTop: 30},
  footerText: {color: Colors.textSub, fontSize: 14},
  signInText: {color: Colors.primary, fontSize: 14, fontWeight: 'bold'},
});

export default SignupScreen;
