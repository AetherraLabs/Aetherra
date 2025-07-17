import { motion } from 'framer-motion';
import { useState } from 'react';

interface PluginSubmissionData {
  name: string;
  description: string;
  author: string;
  email: string;
  version: string;
  category: string;
  tags: string[];
  repositoryUrl: string;
  documentationUrl: string;
  license: string;
  compatibility: string[];
  dependencies: string[];
  screenshots: File[];
  pluginFile: File | null;
  termsAccepted: boolean;
  codeReview: boolean;
  openSource: boolean;
}

interface PluginSubmissionFormProps {
  onSubmit?: (data: PluginSubmissionData) => void;
  onCancel?: () => void;
}

export default function PluginSubmissionForm({ onSubmit, onCancel }: PluginSubmissionFormProps) {
  const [formData, setFormData] = useState<PluginSubmissionData>({
    name: '',
    description: '',
    author: '',
    email: '',
    version: '1.0.0',
    category: '',
    tags: [],
    repositoryUrl: '',
    documentationUrl: '',
    license: 'MIT',
    compatibility: [],
    dependencies: [],
    screenshots: [],
    pluginFile: null,
    termsAccepted: false,
    codeReview: false,
    openSource: false
  });

  const [currentStep, setCurrentStep] = useState(1);
  const [newTag, setNewTag] = useState('');
  const [newCompatibility, setNewCompatibility] = useState('');
  const [newDependency, setNewDependency] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const categories = [
    'AI Enhancement',
    'Development',
    'Performance',
    'Research',
    'Security',
    'Visualization',
    'Data Processing',
    'UI/UX',
    'Integration',
    'Utilities'
  ];

  const licenses = [
    'MIT',
    'Apache-2.0',
    'GPL-3.0',
    'BSD-3-Clause',
    'ISC',
    'Mozilla Public License 2.0',
    'Unlicense',
    'Other'
  ];

  const compatibilityOptions = [
    'Lyrixa 1.8+',
    'Lyrixa 2.0+',
    'Lyrixa 2.1+',
    'AetherOS 1.4+',
    'AetherOS 1.5+',
    'Neural Engine 2.0+',
    'Quantum SDK 1.0+'
  ];

  const handleInputChange = (field: keyof PluginSubmissionData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      handleInputChange('tags', [...formData.tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  const addCompatibility = () => {
    if (newCompatibility && !formData.compatibility.includes(newCompatibility)) {
      handleInputChange('compatibility', [...formData.compatibility, newCompatibility]);
      setNewCompatibility('');
    }
  };

  const removeCompatibility = (compatToRemove: string) => {
    handleInputChange('compatibility', formData.compatibility.filter(compat => compat !== compatToRemove));
  };

  const addDependency = () => {
    if (newDependency.trim() && !formData.dependencies.includes(newDependency.trim())) {
      handleInputChange('dependencies', [...formData.dependencies, newDependency.trim()]);
      setNewDependency('');
    }
  };

  const removeDependency = (depToRemove: string) => {
    handleInputChange('dependencies', formData.dependencies.filter(dep => dep !== depToRemove));
  };

  const handleFileChange = (field: 'screenshots' | 'pluginFile', files: FileList | null) => {
    if (!files) return;

    if (field === 'screenshots') {
      const newScreenshots = Array.from(files).filter(file =>
        file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024 // 5MB limit
      );
      handleInputChange('screenshots', [...formData.screenshots, ...newScreenshots].slice(0, 5));
    } else if (field === 'pluginFile') {
      const file = files[0];
      if (file && (file.name.endsWith('.aether') || file.name.endsWith('.zip'))) {
        handleInputChange('pluginFile', file);
      }
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.name.trim()) newErrors.name = 'Plugin name is required';
        if (!formData.description.trim()) newErrors.description = 'Description is required';
        if (!formData.author.trim()) newErrors.author = 'Author name is required';
        if (!formData.email.trim()) newErrors.email = 'Email is required';
        if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Valid email is required';
        break;

      case 2:
        if (!formData.category) newErrors.category = 'Category is required';
        if (formData.tags.length === 0) newErrors.tags = 'At least one tag is required';
        if (!formData.license) newErrors.license = 'License is required';
        break;

      case 3:
        if (formData.compatibility.length === 0) newErrors.compatibility = 'At least one compatibility requirement is required';
        if (!formData.repositoryUrl.trim()) newErrors.repositoryUrl = 'Repository URL is required';
        break;

      case 4:
        if (!formData.pluginFile) newErrors.pluginFile = 'Plugin file is required';
        if (!formData.termsAccepted) newErrors.termsAccepted = 'You must accept the terms and conditions';
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 4));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(4)) return;

    setIsSubmitting(true);

    try {
      // Simulate submission delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      onSubmit?.(formData);

      // Reset form
      setFormData({
        name: '',
        description: '',
        author: '',
        email: '',
        version: '1.0.0',
        category: '',
        tags: [],
        repositoryUrl: '',
        documentationUrl: '',
        license: 'MIT',
        compatibility: [],
        dependencies: [],
        screenshots: [],
        pluginFile: null,
        termsAccepted: false,
        codeReview: false,
        openSource: false
      });
      setCurrentStep(1);

      alert('Plugin submitted successfully! We will review it and get back to you.');
    } catch (error) {
      alert('Submission failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">Basic Information</h3>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Plugin Name *
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => handleInputChange('name', e.target.value)}
          className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.name ? 'border-red-500' : 'border-gray-600'
            }`}
          placeholder="e.g., Neural Optimizer Pro"
        />
        {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Description *
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={4}
          className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green resize-none ${errors.description ? 'border-red-500' : 'border-gray-600'
            }`}
          placeholder="Describe what your plugin does and its key features..."
        />
        {errors.description && <p className="text-red-400 text-xs mt-1">{errors.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Author Name *
          </label>
          <input
            type="text"
            value={formData.author}
            onChange={(e) => handleInputChange('author', e.target.value)}
            className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.author ? 'border-red-500' : 'border-gray-600'
              }`}
            placeholder="Your name or organization"
          />
          {errors.author && <p className="text-red-400 text-xs mt-1">{errors.author}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Email *
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.email ? 'border-red-500' : 'border-gray-600'
              }`}
            placeholder="your@email.com"
          />
          {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Version
        </label>
        <input
          type="text"
          value={formData.version}
          onChange={(e) => handleInputChange('version', e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          placeholder="1.0.0"
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">Category & Metadata</h3>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Category *
        </label>
        <select
          value={formData.category}
          onChange={(e) => handleInputChange('category', e.target.value)}
          className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.category ? 'border-red-500' : 'border-gray-600'
            }`}
        >
          <option value="">Select a category</option>
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        {errors.category && <p className="text-red-400 text-xs mt-1">{errors.category}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Tags * (helps users find your plugin)
        </label>
        <div className="flex space-x-2 mb-2">
          <input
            type="text"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
            placeholder="Add a tag..."
          />
          <button
            type="button"
            onClick={addTag}
            className="px-4 py-2 bg-aetherra-green text-black rounded hover:bg-green-400 transition-colors"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.tags.map((tag, index) => (
            <span
              key={index}
              className="bg-gray-600 text-white px-2 py-1 rounded text-sm flex items-center space-x-1"
            >
              <span>{tag}</span>
              <button
                onClick={() => removeTag(tag)}
                className="text-red-400 hover:text-red-300"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        {errors.tags && <p className="text-red-400 text-xs mt-1">{errors.tags}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          License *
        </label>
        <select
          value={formData.license}
          onChange={(e) => handleInputChange('license', e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
        >
          {licenses.map(license => (
            <option key={license} value={license}>{license}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Dependencies (optional)
        </label>
        <div className="flex space-x-2 mb-2">
          <input
            type="text"
            value={newDependency}
            onChange={(e) => setNewDependency(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDependency())}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
            placeholder="e.g., neural_engine, data_processor"
          />
          <button
            type="button"
            onClick={addDependency}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-500 transition-colors"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.dependencies.map((dep, index) => (
            <span
              key={index}
              className="bg-blue-600 text-white px-2 py-1 rounded text-sm flex items-center space-x-1"
            >
              <span>{dep}</span>
              <button
                onClick={() => removeDependency(dep)}
                className="text-red-400 hover:text-red-300"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">Compatibility & Links</h3>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Compatibility Requirements *
        </label>
        <div className="flex space-x-2 mb-2">
          <select
            value={newCompatibility}
            onChange={(e) => setNewCompatibility(e.target.value)}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          >
            <option value="">Select compatibility requirement</option>
            {compatibilityOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={addCompatibility}
            className="px-4 py-2 bg-aetherra-green text-black rounded hover:bg-green-400 transition-colors"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.compatibility.map((compat, index) => (
            <span
              key={index}
              className="bg-green-600 text-white px-2 py-1 rounded text-sm flex items-center space-x-1"
            >
              <span>{compat}</span>
              <button
                onClick={() => removeCompatibility(compat)}
                className="text-red-400 hover:text-red-300"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        {errors.compatibility && <p className="text-red-400 text-xs mt-1">{errors.compatibility}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Repository URL *
        </label>
        <input
          type="url"
          value={formData.repositoryUrl}
          onChange={(e) => handleInputChange('repositoryUrl', e.target.value)}
          className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.repositoryUrl ? 'border-red-500' : 'border-gray-600'
            }`}
          placeholder="https://github.com/Zyonic88/plugin-name"
        />
        {errors.repositoryUrl && <p className="text-red-400 text-xs mt-1">{errors.repositoryUrl}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Documentation URL (optional)
        </label>
        <input
          type="url"
          value={formData.documentationUrl}
          onChange={(e) => handleInputChange('documentationUrl', e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          placeholder="https://docs.example.com/plugin-docs"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Screenshots (optional, max 5 files, 5MB each)
        </label>
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={(e) => handleFileChange('screenshots', e.target.files)}
          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
        />
        {formData.screenshots.length > 0 && (
          <div className="mt-2 text-sm text-gray-400">
            {formData.screenshots.length} screenshot(s) selected
          </div>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">Plugin File & Terms</h3>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Plugin File * (.aether or .zip)
        </label>
        <input
          type="file"
          accept=".aether,.zip"
          onChange={(e) => handleFileChange('pluginFile', e.target.files)}
          className={`w-full bg-gray-700 border rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green ${errors.pluginFile ? 'border-red-500' : 'border-gray-600'
            }`}
        />
        {formData.pluginFile && (
          <div className="mt-2 text-sm text-gray-400">
            Selected: {formData.pluginFile.name} ({(formData.pluginFile.size / 1024 / 1024).toFixed(2)} MB)
          </div>
        )}
        {errors.pluginFile && <p className="text-red-400 text-xs mt-1">{errors.pluginFile}</p>}
      </div>

      <div className="space-y-3">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={formData.termsAccepted}
            onChange={(e) => handleInputChange('termsAccepted', e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-300">
            I accept the <a href="/terms" className="text-aetherra-green hover:underline">Terms and Conditions</a> and
            <a href="/plugin-guidelines" className="text-aetherra-green hover:underline ml-1">Plugin Guidelines</a> *
          </span>
        </label>
        {errors.termsAccepted && <p className="text-red-400 text-xs">{errors.termsAccepted}</p>}

        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={formData.codeReview}
            onChange={(e) => handleInputChange('codeReview', e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-300">
            I consent to code review and security scanning
          </span>
        </label>

        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={formData.openSource}
            onChange={(e) => handleInputChange('openSource', e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-300">
            This plugin is open source
          </span>
        </label>
      </div>

      <div className="bg-blue-900 border border-blue-600 rounded p-4">
        <h4 className="font-semibold text-blue-300 mb-2">📋 Review Process</h4>
        <ul className="text-sm text-blue-200 space-y-1">
          <li>• Your plugin will be reviewed within 5-7 business days</li>
          <li>• We'll test compatibility and security</li>
          <li>• You'll receive feedback via email</li>
          <li>• Approved plugins appear in the gallery within 24 hours</li>
        </ul>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-aetherra-green">
            📦 Submit Plugin to AetherHub
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mt-4 space-x-4">
          {[1, 2, 3, 4].map(step => (
            <div key={step} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === currentStep
                  ? 'bg-aetherra-green text-black'
                  : step < currentStep
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-600 text-gray-300'
                }`}>
                {step < currentStep ? '✓' : step}
              </div>
              {step < 4 && (
                <div className={`w-8 h-0.5 ${step < currentStep ? 'bg-green-600' : 'bg-gray-600'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="text-center mt-2 text-sm text-gray-400">
          Step {currentStep} of 4
        </div>
      </div>

      {/* Form Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </motion.div>
      </div>

      {/* Navigation */}
      <div className="p-4 border-t border-gray-700 bg-gray-800 rounded-b-xl">
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 1}
            className={`px-4 py-2 rounded font-medium transition-colors ${currentStep === 1
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gray-700 text-white hover:bg-gray-600'
              }`}
          >
            ← Previous
          </button>

          {currentStep < 4 ? (
            <button
              onClick={nextStep}
              className="px-4 py-2 bg-aetherra-green text-black rounded font-medium hover:bg-green-400 transition-colors"
            >
              Next →
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className={`px-6 py-2 rounded font-medium transition-colors ${isSubmitting
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-aetherra-green text-black hover:bg-green-400'
                }`}
            >
              {isSubmitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  <span>Submitting...</span>
                </div>
              ) : (
                '📤 Submit Plugin'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
