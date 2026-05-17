import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    TouchableOpacity,
    TextInput,
    Image,
    StatusBar,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { ArrowLeft, Camera, User, Mail, Phone, Check } from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '../theme/Colors';
import { translations, Language } from '../utils/translations';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { launchImageLibrary } from 'react-native-image-picker';
import { updateProfile } from '../services/api.service';

type Props = NativeStackScreenProps<RootStackParamList, 'EditProfile'>;

export default function EditProfileScreen({ navigation }: Props) {
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [language, setLanguage] = useState<Language>('en');
    const [loading, setLoading] = useState(false);

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [avatar, setAvatar] = useState('https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const mode = await AsyncStorage.getItem('darkMode');
            const lang = await AsyncStorage.getItem('language');
            const userJson = await AsyncStorage.getItem('user');

            if (mode) setIsDarkMode(JSON.parse(mode));
            if (lang) setLanguage(lang as Language);
            if (userJson) {
                const userData = JSON.parse(userJson);
                setName(userData.full_name || userData.name || '');
                setEmail(userData.email || '');
                setPhone(userData.phone || '');
                if (userData.avatar) setAvatar(userData.avatar);
            }
        } catch (e) {
            console.error('Error loading profile data', e);
        }
    };

    const t = translations[language];

    const pickImage = async () => {
        const result = await launchImageLibrary({
            mediaType: 'photo',
            quality: 0.8,
            selectionLimit: 1,
        });

        if (result.assets && result.assets[0].uri) {
            setAvatar(result.assets[0].uri);
        }
    };

    const handleSave = async () => {
        if (!name.trim()) {
            Alert.alert("Error", "Name cannot be empty");
            return;
        }

        setLoading(true);
        try {
            const userJson = await AsyncStorage.getItem('user');
            if (userJson) {
                const userData = JSON.parse(userJson);

                // Save to backend
                await updateProfile(userData.id, name, email);

                const updatedUser = {
                    ...userData,
                    full_name: name,
                    name: name,
                    email: email,
                    phone: phone,
                    avatar: avatar
                };
                await AsyncStorage.setItem('user', JSON.stringify(updatedUser));

                Alert.alert(
                    "Success",
                    "Profile updated successfully!",
                    [{ text: "OK", onPress: () => navigation.goBack() }]
                );
            }
        } catch (e: any) {
            console.error(e);
            Alert.alert("Error", e.message || "Failed to update profile. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView style={[styles.container, isDarkMode && styles.containerDark]}>
            <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />

            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <ArrowLeft size={24} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
                </TouchableOpacity>
                <Text style={[styles.headerTitle, isDarkMode && { color: '#F8FAFC' }]}>Edit Profile</Text>
                <TouchableOpacity
                    style={styles.saveBtnTop}
                    onPress={handleSave}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator size="small" color={Colors.primary} />
                    ) : (
                        <Check size={24} color={Colors.primary} />
                    )}
                </TouchableOpacity>
            </View>

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.avatarSection}>
                    <TouchableOpacity
                        style={styles.avatarContainer}
                        onPress={pickImage}
                        activeOpacity={0.8}
                    >
                        <Image
                            source={{ uri: avatar }}
                            style={styles.avatar}
                        />
                        <View style={styles.cameraIcon}>
                            <Camera size={16} color="#FFF" />
                        </View>
                    </TouchableOpacity>
                    <Text style={[styles.avatarTip, isDarkMode && { color: '#94A3B8' }]}>
                        Tap to change profile picture
                    </Text>
                </View>

                <View style={styles.form}>
                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Full Name</Text>
                        <View style={[styles.inputWrapper, isDarkMode && styles.inputWrapperDark]}>
                            <User size={18} color="#94A3B8" style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, isDarkMode && { color: '#F8FAFC' }]}
                                value={name}
                                onChangeText={setName}
                                placeholder="Enter your name"
                                placeholderTextColor="#94A3B8"
                            />
                        </View>
                    </View>

                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Email Address</Text>
                        <View style={[styles.inputWrapper, isDarkMode && styles.inputWrapperDark]}>
                            <Mail size={18} color="#94A3B8" style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, isDarkMode && { color: '#F8FAFC' }]}
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                                placeholder="Enter your email"
                                placeholderTextColor="#94A3B8"
                            />
                        </View>
                    </View>

                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Phone Number</Text>
                        <View style={[styles.inputWrapper, isDarkMode && styles.inputWrapperDark]}>
                            <Phone size={18} color="#94A3B8" style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, isDarkMode && { color: '#F8FAFC' }]}
                                value={phone}
                                onChangeText={setPhone}
                                keyboardType="phone-pad"
                                placeholder="Enter your phone number"
                                placeholderTextColor="#94A3B8"
                            />
                        </View>
                    </View>
                </View>

                <TouchableOpacity
                    style={[styles.saveBtnLarge, loading && { opacity: 0.7 }]}
                    onPress={handleSave}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#FFF" />
                    ) : (
                        <Text style={styles.saveBtnText}>Save Changes</Text>
                    )}
                </TouchableOpacity>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F8FAFC' },
    containerDark: { backgroundColor: '#0F172A' },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 20,
        paddingVertical: 15,
    },
    backBtn: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
    headerTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
    saveBtnTop: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center' },
    content: { padding: 20 },
    avatarSection: { alignItems: 'center', marginBottom: 30 },
    avatarContainer: { width: 100, height: 100, borderRadius: 50, position: 'relative' },
    avatar: { width: '100%', height: '100%', borderRadius: 50 },
    cameraIcon: {
        position: 'absolute',
        bottom: 0,
        right: 0,
        backgroundColor: Colors.primary,
        width: 32,
        height: 32,
        borderRadius: 16,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 3,
        borderColor: '#FFF',
    },
    avatarTip: { fontSize: 12, color: '#64748B', marginTop: 10 },
    form: { gap: 20 },
    inputGroup: { gap: 8 },
    label: { fontSize: 14, fontWeight: 'bold', color: '#64748B', marginLeft: 4 },
    inputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFF',
        borderRadius: 15,
        borderWidth: 1,
        borderColor: '#F1F5F9',
        paddingHorizontal: 15,
        height: 56,
    },
    inputWrapperDark: { backgroundColor: '#1E293B', borderColor: '#334155' },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: Colors.textHeader },
    saveBtnLarge: {
        backgroundColor: Colors.primary,
        height: 56,
        borderRadius: 15,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 40,
        elevation: 4,
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
    },
    saveBtnText: { color: '#FFF', fontSize: 18, fontWeight: 'bold' },
});
