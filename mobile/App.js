import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Image, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as ImagePicker from 'expo-image-picker';
import { useState } from 'react';
import axios from 'axios';

import { API_URL } from './config';

// ------------------------------------------------------------------
// CONFIGURATION
// ------------------------------------------------------------------
// Configuration is now handled in config.js
// Toggle IS_PRODUCTION to true in config.js when building APK

export default function App() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    // Request permission
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'We need camera roll permissions to make this work!');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setResult(null); // Reset previous result
      analyzeImage(result.assets[0]);
    }
  };

  const analyzeImage = async (imageAsset) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: imageAsset.uri,
        name: 'leaf.jpg',
        type: 'image/jpeg',
      });

      const response = await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Failed to analyze image. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient
        colors={['#166534', '#15803d']} // Green-800 to Green-700
        style={styles.header}
      >
        <Text style={styles.title}>Medicinal Plant AI</Text>
        <Text style={styles.subtitle}>Instant Identification</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.content}>

        {/* Image Preview / Placeholder */}
        <View style={styles.card}>
          {image ? (
            <Image source={{ uri: image }} style={styles.image} />
          ) : (
            <View style={styles.placeholder}>
              <Text style={styles.placeholderIcon}>🌿</Text>
              <Text style={styles.placeholderText}>Tap to scan a leaf</Text>
            </View>
          )}

          {loading && (
            <View style={styles.loadingOverlay}>
              <ActivityIndicator size="large" color="#ffffff" />
              <Text style={styles.loadingText}>Analyzing Structure...</Text>
            </View>
          )}
        </View>

        {/* Action Button */}
        <TouchableOpacity
          style={styles.button}
          onPress={pickImage}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {image ? 'Scan Another' : 'Select Image'}
          </Text>
        </TouchableOpacity>

        {/* Results */}
        {result && (
          <View style={styles.resultCard}>
            <Text style={styles.matchTitle}>Best Match</Text>
            <Text style={styles.plantName}>
              {result.predicted_plant?.replace(/_/g, ' ')}
            </Text>

            <View style={styles.confidenceRow}>
              <View style={styles.progressBarBg}>
                <View
                  style={[
                    styles.progressBarFill,
                    { width: `${result.confidence * 100}%` }
                  ]}
                />
              </View>
              <Text style={styles.confidenceText}>
                {(result.confidence * 100).toFixed(1)}%
              </Text>
            </View>

            {result.plant_details && (
              <View style={styles.details}>
                <Text style={styles.detailsText}>
                  {result.plant_details.common_name}
                </Text>
              </View>
            )}
          </View>
        )}

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 16,
    color: '#dcfce7',
    marginTop: 5,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
    marginBottom: 20,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholder: {
    alignItems: 'center',
  },
  placeholderIcon: {
    fontSize: 60,
    marginBottom: 10,
    opacity: 0.5,
  },
  placeholderText: {
    fontSize: 18,
    color: '#9ca3af',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#ffffff',
    marginTop: 10,
    fontSize: 16,
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#16a34a',
    paddingVertical: 18,
    borderRadius: 15,
    alignItems: 'center',
    shadowColor: '#16a34a',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 6,
    marginBottom: 20,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultCard: {
    backgroundColor: '#ffffff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  matchTitle: {
    fontSize: 14,
    color: '#6b7280',
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 5,
  },
  plantName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 15,
  },
  confidenceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  progressBarBg: {
    flex: 1,
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    marginRight: 10,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#16a34a',
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 14,
    color: '#4b5563',
    fontWeight: '600',
    width: 45,
    textAlign: 'right',
  },
  details: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  detailsText: {
    color: '#4b5563',
    fontSize: 16,
  }
});
