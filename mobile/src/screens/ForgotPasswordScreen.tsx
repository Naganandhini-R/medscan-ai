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
  Alert,
  ActivityIndicator,
} from 'react-native';
import {Mail, Lock, ArrowLeft, ShieldCheck} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import {resetPassword} from '../services/api.service';
import {Colors} from '../theme/Colors';

const ForgotPasswordScreen = ({navigation}: any) => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleReset = async () => {
    if (!email || !newPassword) {
      Alert.alert('Error', 'Please enter your email and a new password');
      return;
    }

    setLoading(true);
    try {
      await resetPassword(email, newPassword);
      Alert.alert(
        'Success',
        'Password has been reset successfully! You can now sign in.',
        [{text: 'OK', onPress: () => navigation.navigate('Login')}],
      );
    } catch (e: any) {
      Alert.alert(
        'Reset Failed',
        e.message || 'Verification failed. Ensure the email is correct.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
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
            <View style={styles.iconCircle}>
              <LinearGradient
                colors={['#2196F3', '#0D47A1']}
                style={styles.logoGradient}>
                <ShieldCheck size={32} color="#FFF" />
              </LinearGradient>
            </View>
            <Text style={styles.title}>Reset Credentials</Text>
            <Text style={styles.subtitle}>
              Enter your registered email and a new secure password.
            </Text>
          </Animatable.View>

          <Animatable.View
            animation="fadeInUp"
            delay={300}
            style={styles.formContainer}>
            <View style={styles.inputGroup}>
              <View style={styles.inputWrapper}>
                <Mail
                  size={20}
                  color={Colors.textSub}
                  style={styles.inputIcon}
                />
                <TextInput
                  placeholder="Registered Email"
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
                  placeholder="New Secure Password"
                  value={newPassword}
                  onChangeText={setNewPassword}
                  secureTextEntry
                  style={styles.input}
                  placeholderTextColor={Colors.textSub}
                />
              </View>
            </View>

            <TouchableOpacity
              onPress={handleReset}
              style={[styles.resetButton, loading && {opacity: 0.7}]}
              disabled={loading}>
              <LinearGradient
                colors={['#2196F3', '#42A5F5']}
                start={{x: 0, y: 0}}
                end={{x: 1, y: 0}}
                style={styles.buttonGradient}>
                {loading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <Text style={styles.buttonText}>Update Password</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>
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
  header: {alignItems: 'center', marginBottom: 40},
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    overflow: 'hidden',
    marginBottom: 16,
  },
  logoGradient: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  title: {fontSize: 26, fontWeight: 'bold', color: Colors.textHeader},
  subtitle: {
    fontSize: 14,
    color: Colors.textSub,
    textAlign: 'center',
    marginTop: 8,
    paddingHorizontal: 20,
  },
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
  resetButton: {
    marginTop: 40,
    height: 56,
    borderRadius: 12,
    overflow: 'hidden',
  },
  buttonGradient: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  buttonText: {color: '#FFF', fontSize: 18, fontWeight: 'bold'},
});

export default ForgotPasswordScreen;
