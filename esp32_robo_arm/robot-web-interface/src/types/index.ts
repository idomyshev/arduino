// Types for Robot Arm Web Interface

export interface MotorState {
  id: number;
  name: string;
  position: number; // 0-100%
  speed: number; // 0-255
  isMoving: boolean;
}

export interface MotorCommand {
  motor: number;
  direction: 'forward' | 'backward';
  speed: number;
  duration?: number;
}

export interface WebSocketMessage {
  type: 'connection_status' | 'motor_command' | 'error' | 'status';
  message?: string;
  connected?: boolean;
  success?: boolean;
  robot_connected?: boolean;
}

export interface CalibrationData {
  motorId: number;
  forwardTime: number;
  backwardTime: number;
  calibrated: boolean;
  calibrationDate: string;
}

export interface RobotConnection {
  connected: boolean;
  connecting: boolean;
  error?: string;
}

// Motor definitions
export const MOTORS = [
  { id: 0, name: 'Малое плечо', shortName: 'M1', icon: '🦾' },
  { id: 1, name: 'Большое плечо', shortName: 'M2', icon: '🦿' },
  { id: 2, name: 'Клешня', shortName: 'M3', icon: '🦀' }
] as const;

// Motor button configurations
export const MOTOR_BUTTONS = {
  0: { // Малое плечо
    left: { label: 'Опустить', direction: 'backward' as const },
    right: { label: 'Поднять', direction: 'forward' as const }
  },
  1: { // Большое плечо
    left: { label: 'Поднять', direction: 'backward' as const },
    right: { label: 'Опустить', direction: 'forward' as const }
  },
  2: { // Клешня
    left: { label: 'Закрыть', direction: 'backward' as const },
    right: { label: 'Открыть', direction: 'forward' as const }
  }
} as const;

// Re-export all types for easier importing
export type {
  MotorState,
  MotorCommand,
  WebSocketMessage,
  CalibrationData,
  RobotConnection
};
