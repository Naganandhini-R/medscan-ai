import React, { useState } from 'react';
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
  Alert,
  ActivityIndicator,
  Modal,
} from 'react-native';
import {
  Mail,
  Lock,
  Apple,
  Chrome as Google,
  Eye,
  EyeOff,
  User as UserIcon,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { login, googleLogin } from '../services/api.service';
import { Colors } from '../theme/Colors';

const LoginScreen = ({ navigation }: any) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showGooglePicker, setShowGooglePicker] = useState(false);

  const mockAccounts: any[] = [];

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setLoading(true);
    try {
      const data = await login(email, password);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));

      if (data.user.has_boarded) {
        navigation.replace('Home');
      } else {
        navigation.replace('Onboarding');
      }
    } catch (e: any) {
      Alert.alert(
        'Login Failed',
        e.message || 'Invalid email or password. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async (selectedAccount: any) => {
    setShowGooglePicker(false);
    setLoading(true);
    try {
      const data = await googleLogin(selectedAccount.email, selectedAccount.name);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));

      if (data.user.has_boarded) {
        navigation.replace('Home');
      } else {
        navigation.replace('Onboarding');
      }
    } catch (e: any) {
      Alert.alert('Google Auth Error', e.message || 'Failed to authenticate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <Animatable.View animation="fadeInDown" style={styles.header}>
            <View style={styles.logoCircle}>
              <LinearGradient
                colors={['#2196F3', '#0D47A1']}
                style={styles.logoGradient}>
                <Text style={styles.logoText}>+</Text>
              </LinearGradient>
            </View>
            <Text style={styles.brandName}>MedScan-AI</Text>
          </Animatable.View>

          <Animatable.View
            animation="fadeInUp"
            delay={300}
            style={styles.formContainer}>
            <Text style={styles.title}>Sign In</Text>
            <Text style={styles.subtitle}>
              Welcome to MedScan-AI! Please sign in to continue.
            </Text>

            <View style={styles.inputGroup}>
              <View style={styles.inputWrapper}>
                <Mail
                  size={20}
                  color={Colors.textSub}
                  style={styles.inputIcon}
                />
                <TextInput
                  placeholder="Email"
                  value={email}
                  onChangeText={setEmail}
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
              <TouchableOpacity
                onPress={() => navigation.navigate('ForgotPassword')}
                style={styles.forgotPasswordContainer}
                activeOpacity={0.7}>
                <Text style={styles.forgotText}>Forgot Password?</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              onPress={handleLogin}
              style={[styles.signInButton, loading && { opacity: 0.7 }]}
              disabled={loading}>
              <LinearGradient
                colors={['#2196F3', '#42A5F5']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.buttonGradient}>
                {loading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <Text style={styles.buttonText}>Sign In</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <View style={styles.dividerContainer}>
              <View style={styles.divider} />
              <Text style={styles.orText}>Or</Text>
              <View style={styles.divider} />
            </View>

            <View style={styles.socialContainer}>
              <TouchableOpacity
                style={styles.socialButton}
                onPress={() => setShowGooglePicker(true)}>
                <Google size={24} color="#5F6368" />
                <Text style={styles.socialText}>Continue with Google</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.socialButton, { backgroundColor: '#000' }]}>
                <Apple size={24} color="#FFF" />
                <Text style={[styles.socialText, { color: '#FFF' }]}>
                  Continue with Apple
                </Text>
              </TouchableOpacity>
            </View>

            <View style={styles.footer}>
              <Text style={styles.footerText}>Don't have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Signup')}>
                <Text style={styles.signUpText}>Sign Up</Text>
              </TouchableOpacity>
            </View>
          </Animatable.View>
        </ScrollView>
      </KeyboardAvoidingView>

      <Modal
        visible={showGooglePicker}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowGooglePicker(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.pickerContainer}>
            <View style={styles.pickerHeader}>
              <Google size={24} color="#4285F4" />
              <Text style={styles.pickerTitle}>Choose an account</Text>
              <Text style={styles.pickerSubtitle}>to continue to MedScan-AI</Text>
            </View>

            <View style={styles.accountsList}>
              {mockAccounts.map((account, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.accountItem}
                  onPress={() => handleGoogleLogin(account)}>
                  <View style={styles.accountAvatar}>
                    <UserIcon size={20} color="#5F6368" />
                  </View>
                  <View>
                    <Text style={styles.accountName}>{account.name}</Text>
                    <Text style={styles.accountEmail}>{account.email}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setShowGooglePicker(false)}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollContent: {
    padding: 24,
    flexGrow: 1,
  },
  header: {
    alignItems: 'center',
    marginTop: 40,
    marginBottom: 40,
  },
  logoCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    overflow: 'hidden',
    marginBottom: 10,
  },
  logoGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoText: {
    color: '#FFF',
    fontSize: 40,
    fontWeight: '300',
  },
  brandName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: Colors.darkBlue,
  },
  formContainer: {
    flex: 1,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.textHeader,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textSub,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 30,
  },
  inputGroup: {
    gap: 16,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 56,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: Colors.textHeader,
    height: '100%',
  },
  eyeIcon: {
    padding: 4,
  },
  forgotPasswordContainer: {
    alignSelf: 'flex-end',
    marginTop: 4,
    paddingBottom: 8,
  },
  forgotText: {
    color: Colors.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  signInButton: {
    marginTop: 30,
    height: 56,
    borderRadius: 12,
    overflow: 'hidden',
  },
  buttonGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 30,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: '#E2E8F0',
  },
  orText: {
    marginHorizontal: 16,
    color: Colors.textSub,
    fontSize: 14,
  },
  socialContainer: {
    gap: 16,
  },
  socialButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: 12,
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  socialText: {
    marginLeft: 12,
    fontSize: 16,
    fontWeight: '600',
    color: '#5F6368',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 30,
    marginBottom: 20,
  },
  footerText: {
    color: Colors.textSub,
    fontSize: 14,
  },
  signUpText: {
    color: Colors.primary,
    fontSize: 14,
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  pickerContainer: {
    backgroundColor: '#FFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
  },
  pickerHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  pickerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#202124',
    marginTop: 12,
  },
  pickerSubtitle: {
    fontSize: 14,
    color: '#5F6368',
    marginTop: 4,
  },
  accountsList: {
    marginBottom: 20,
  },
  accountItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F3F4',
  },
  accountAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F1F3F4',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  accountName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3C4043',
  },
  accountEmail: {
    fontSize: 12,
    color: '#5F6368',
  },
  cancelButton: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  cancelText: {
    fontSize: 14,
    color: '#1A73E8',
    fontWeight: 'bold',
  },
});

export default LoginScreen;
