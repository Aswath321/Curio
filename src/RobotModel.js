import React, { useRef, useEffect, useState } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { Canvas, useFrame } from '@react-three/fiber';

const RobotModel = () => {
  const group = useRef();
  const { scene, animations } = useGLTF('/robo.glb', true);
  const { actions } = useAnimations(animations, group);
  
  const [animationState, setAnimationState] = useState('idle');

  useEffect(() => {
    if (actions['idle']) {
      actions['idle'].play();
    }
  }, [actions]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    
    // Apply rotation and translation for dynamic movements
    group.current.rotation.y = Math.sin(t / 2) * Math.PI / 8;
    group.current.position.y = Math.sin(t * 2) / 2;

    // Adjust arm positions
    const leftArm = group.current.getObjectByName('LeftArm'); // Replace with actual bone name
    const rightArm = group.current.getObjectByName('RightArm'); // Replace with actual bone name
    
    if (leftArm && rightArm) {
      // Modify arm positions or rotations
      leftArm.rotation.z = Math.sin(t * 2) * 0.2;  // Adjust arm rotation
      rightArm.rotation.z = Math.cos(t * 2) * 0.2; // Adjust arm rotation
    }

    // Switch animations every few seconds
    if (Math.floor(t) % 4 === 0) {
      switchAnimation();
    }
  });

  const switchAnimation = () => {
    if (actions[animationState]) {
      actions[animationState].stop();
    }

    const animationsList = ['dance', 'flip', 'wave', 'idle'];
    const newAnimation = animationsList[Math.floor(Math.random() * animationsList.length)];

    if (actions[newAnimation]) {
      actions[newAnimation].play();
      setAnimationState(newAnimation);
    }
  };

  return (
    <group ref={group}>
      <primitive object={scene} scale={1.5} position={[0, -1.5, 0]} />
    </group>
  );
};

export const RobotCanvas = () => {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 75 }}
      style={{ width: '100%', height: '100%' }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[0, 5, 5]} />
      <RobotModel />
    </Canvas>
  );
};

export default RobotModel;
