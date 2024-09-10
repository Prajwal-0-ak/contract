import React, { useState, useEffect } from 'react';
import {  FileText, Database, Brain, Send } from 'lucide-react';

// Common Overlay Component
const Overlay: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="fixed inset-0 flex items-center justify-center z-50">
    <div className="absolute inset-0 bg-gray-800 bg-opacity-75"></div>
    <div className="z-10">{children}</div>
  </div>
);

// Version 1: Animated Step Progress
const LoadingSpinnerV1: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const steps = [
    { icon: Send, label: 'Sending to Backend' },
    { icon: FileText, label: 'Chunking Content' },
    { icon: Database, label: 'Embedding Content' },
    { icon: Database, label: 'Storing in Vector DB' },
    { icon: Brain, label: 'Analyzing' },
    { icon: FileText, label: 'Extracting Fields' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <Overlay>
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4 text-center text-black">Processing Your Document</h2>
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                index === currentStep ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                <step.icon className="w-5 h-5" />
              </div>
              <div className="ml-4 flex-grow">
                <div className="h-2 bg-gray-200 rounded">
                  <div 
                    className="h-2 bg-blue-500 rounded" 
                    style={{ 
                      width: index === currentStep ? '100%' : '0%',
                      transition: 'width 3s linear'
                    }}
                  />
                </div>
              </div>
              <span className="ml-2 text-sm text-black">{step.label}</span>
            </div>
          ))}
        </div>
      </div>
    </Overlay>
  );
};

// Version 2: Circular Progress with Fun Facts
const LoadingSpinnerV2: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [factIndex, setFactIndex] = useState(0);

  const funFacts = [
    "Did you know? The first computer bug was an actual insect!",
    "The term 'robot' comes from the Czech word 'robota', meaning 'forced labor'.",
    "The first computer mouse was made of wood!",
    "The first electronic computer ENIAC weighed more than 27 tons!",
    "A 'jiffy' is an actual unit of time: 1/100th of a second.",
    "The first 1GB hard disk drive was announced in 1980 and weighed about 550 pounds.",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev + 1) % 101);
      if (progress % 20 === 0) {
        setFactIndex((prev) => (prev + 1) % funFacts.length);
      }
    }, 200);
    return () => clearInterval(interval);
  }, [progress, funFacts.length]);

  return (
    <Overlay>
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4 text-center text-black">Processing Your Document</h2>
        <div className="relative w-48 h-48 mx-auto mb-4">
          <svg className="w-full h-full" viewBox="0 0 100 100">
            <circle
              className="text-gray-200 stroke-current"
              strokeWidth="8"
              cx="50"
              cy="50"
              r="40"
              fill="transparent"
            ></circle>
            <circle
              className="text-blue-500 progress-ring__circle stroke-current"
              strokeWidth="8"
              strokeLinecap="round"
              cx="50"
              cy="50"
              r="40"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 40}`}
              strokeDashoffset={`${2 * Math.PI * 40 * (1 - progress / 100)}`}
            ></circle>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold text-black">{progress}%</span>
          </div>
        </div>
        <div className="text-center text-sm text-black h-12">
          <p>{funFacts[factIndex]}</p>
        </div>
      </div>
    </Overlay>
  );
};

// Version 3: Animated Document Processing
const LoadingSpinnerV3: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const steps = [
    { icon: Send, label: 'Sending' },
    { icon: FileText, label: 'Chunking' },
    { icon: Database, label: 'Embedding' },
    { icon: Database, label: 'Storing' },
    { icon: Brain, label: 'Analyzing' },
    { icon: FileText, label: 'Extracting' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <Overlay>
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4 text-center text-black">Processing Your Document</h2>
        <div className="relative w-64 h-64">
          <div className="absolute inset-0 flex items-center justify-center">
            <FileText className="w-32 h-32 text-gray-300" />
          </div>
          <div className="absolute inset-0">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`absolute inset-0 flex items-center justify-center transition-opacity duration-500 ${
                  index === currentStep ? 'opacity-100' : 'opacity-0'
                }`}
                style={{ transform: `rotate(${index * 60}deg)` }}
              >
                <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center animate-bounce">
                  <step.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="text-center mt-4">
          <p className="text-lg font-semibold text-black">{steps[currentStep].label}</p>
          <p className="text-sm text-gray-600">Please wait while we process your document</p>
        </div>
      </div>
    </Overlay>
  );
};

export { LoadingSpinnerV1, LoadingSpinnerV2, LoadingSpinnerV3 };