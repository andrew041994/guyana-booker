import React, { useState } from 'react';
import { Text, View, StyleSheet, TextInput, Button, Alert } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import axios from 'axios';
import { registerRootComponent } from 'expo';

const API = 'http://192.168.1.100:8000'; // CHANGE TO YOUR PC IP

const Tab = createBottomTabNavigator();

function LoginScreen({ setToken }) {
  const [email, setEmail] = useState('customer@guyana.com');
  const [password, setPassword] = useState('pass');

  const login = async () => {
    try {
      const res = await axios.post(`${API}/auth/login`, new URLSearchParams({
        username: email,
        password: password
      }));
      setToken(res.data.access_token);
      Alert.alert('Success', 'Logged in!');
    } catch (e) {
      Alert.alert('Login Failed', 'Wrong email or password');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Guyana Booker</Text>
      <TextInput style={styles.input} placeholder="Email" value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Login" onPress={login} color="#16a34a" />
    </View>
  );
}

function SignupScreen({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');

  const signup = async () => {
    try {
      await axios.post(`${API}/auth/signup`, {
        email, password, full_name: name, phone, location: "Georgetown", whatsapp: `whatsapp:+592${phone}`
      });
      Alert.alert('Success', 'Account created! Now login');
    } catch (e) {
      Alert.alert('Error', e.response?.data?.detail || 'Try again');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      <TextInput style={styles.input} placeholder="Full Name" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <TextInput style={styles.input} placeholder="Phone (592XXXXXXX)" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
      <TextInput style={styles.input} placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Sign Up" onPress={signup} color="#16a34a" />
    </View>
  );
}

function MainApp({ token }) {
  return (
    <NavigationContainer>
      <Tab.Navigator screenOptions={{ headerShown: false }}>
        <Tab.Screen name="Home" component={HomeScreen} />
        <Tab.Screen name="Search" component={SearchScreen} />
        <Tab.Screen name="Admin" component={AdminScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

function App() {
  const [token, setToken] = useState(null);

  if (!token) {
    return <LoginScreen setToken={setToken} />;
  }

  return <MainApp token={token} />;
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4', justifyContent: 'center', alignItems: 'center', padding: 20 },
  title: { fontSize: 36, fontWeight: 'bold', color: '#16a34a' },
  subtitle: { fontSize: 22, color: '#166534', marginTop: 20 },
  text: { fontSize: 18, color: '#166534', marginTop: 15, textAlign: 'center' },
});

registerRootComponent(App);