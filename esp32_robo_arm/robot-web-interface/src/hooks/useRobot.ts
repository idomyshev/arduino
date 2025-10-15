// Custom hook for robot state management
import { useState, useEffect, useCallback } from 'react';
import { RobotWebSocketService } from '../services/websocket.js';
import { MotorState, RobotConnection, WebSocketMessage, MotorCommand } from '../types/index.js';

export const useRobot = () => {
  const [connection, setConnection] = useState<RobotConnection>({
    connected: false,
    connecting: false
  });
  
  const [motors, setMotors] = useState<MotorState[]>([
    { id: 0, name: 'Малое плечо', position: 0, speed: 200, isMoving: false },
    { id: 1, name: 'Большое плечо', position: 0, speed: 200, isMoving: false },
    { id: 2, name: 'Клешня', position: 0, speed: 200, isMoving: false }
  ]);

  const [wsService] = useState(() => new RobotWebSocketService());

  useEffect(() => {
    // Handle WebSocket messages
    wsService.onMessage((message: WebSocketMessage) => {
      switch (message.type) {
        case 'connection_status':
          setConnection(prev => ({
            ...prev,
            connected: message.connected || false,
            connecting: false,
            error: message.message
          }));
          break;
          
        case 'motor_command':
          if (message.success) {
            console.log('Motor command executed:', message.message);
          }
          break;
          
        case 'error':
          setConnection(prev => ({
            ...prev,
            error: message.message,
            connecting: false
          }));
          break;
          
        case 'status':
          setConnection(prev => ({
            ...prev,
            connected: message.robot_connected || false,
            connecting: false
          }));
          break;
      }
    });

    // Handle connection changes
    wsService.onConnectionChange((connected: boolean) => {
      setConnection(prev => ({
        ...prev,
        connected,
        connecting: false
      }));
    });

    return () => {
      wsService.close();
    };
  }, [wsService]);

  const connectToRobot = useCallback(() => {
    setConnection(prev => ({ ...prev, connecting: true, error: undefined }));
    wsService.connectToRobot();
  }, [wsService]);

  const disconnectFromRobot = useCallback(() => {
    wsService.disconnectFromRobot();
  }, [wsService]);

  const moveMotor = useCallback((motorId: number, direction: 'forward' | 'backward', speed?: number, duration?: number) => {
    const motor = motors.find(m => m.id === motorId);
    if (!motor) return;

    const motorSpeed = speed || motor.speed;
    
    // Update motor state
    setMotors(prev => prev.map(m => 
      m.id === motorId 
        ? { ...m, isMoving: true, speed: motorSpeed }
        : m
    ));

    wsService.moveMotor(motorId, direction, motorSpeed, duration);
  }, [motors, wsService]);

  const stopMotor = useCallback((motorId: number) => {
    setMotors(prev => prev.map(m => 
      m.id === motorId 
        ? { ...m, isMoving: false }
        : m
    ));
    
    wsService.stopMotor(motorId);
  }, [wsService]);

  const stopAllMotors = useCallback(() => {
    setMotors(prev => prev.map(m => ({ ...m, isMoving: false })));
    wsService.stopAllMotors();
  }, [wsService]);

  const updateMotorSpeed = useCallback((motorId: number, speed: number) => {
    setMotors(prev => prev.map(m => 
      m.id === motorId 
        ? { ...m, speed }
        : m
    ));
  }, []);

  const updateMotorPosition = useCallback((motorId: number, position: number) => {
    setMotors(prev => prev.map(m => 
      m.id === motorId 
        ? { ...m, position }
        : m
    ));
  }, []);

  return {
    connection,
    motors,
    connectToRobot,
    disconnectFromRobot,
    moveMotor,
    stopMotor,
    stopAllMotors,
    updateMotorSpeed,
    updateMotorPosition,
    isConnected: wsService.isConnected()
  };
};
