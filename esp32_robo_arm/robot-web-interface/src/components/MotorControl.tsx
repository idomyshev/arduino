// Motor Control Component
import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Button,
  Slider,
  Box,
  Chip,
  Stack,
} from "@mui/material";
import {
  PlayArrow,
  Stop,
  KeyboardArrowUp,
  KeyboardArrowDown,
  OpenInFull,
} from "@mui/icons-material";
import { MotorState, MOTOR_BUTTONS } from "../types/index.js";

interface MotorControlProps {
  motor: MotorState;
  onMoveMotor: (
    motorId: number,
    direction: "forward" | "backward",
    speed?: number,
  ) => void;
  onStopMotor: (motorId: number) => void;
  onSpeedChange: (motorId: number, speed: number) => void;
  disabled?: boolean;
}

const MotorControl: React.FC<MotorControlProps> = ({
  motor,
  onMoveMotor,
  onStopMotor,
  onSpeedChange,
  disabled = false,
}) => {
  const motorConfig = MOTOR_BUTTONS[motor.id as keyof typeof MOTOR_BUTTONS];

  const getMotorIcon = () => {
    switch (motor.id) {
      case 0:
        return <KeyboardArrowUp />; // Малое плечо
      case 1:
        return <KeyboardArrowDown />; // Большое плечо
      case 2:
        return <OpenInFull />; // Клешня
      default:
        return <PlayArrow />;
    }
  };

  const handleLeftButtonClick = () => {
    onMoveMotor(motor.id, motorConfig.left.direction, motor.speed);
  };

  const handleRightButtonClick = () => {
    onMoveMotor(motor.id, motorConfig.right.direction, motor.speed);
  };

  const handleStopClick = () => {
    onStopMotor(motor.id);
  };

  const handleSpeedChange = (_: Event, newValue: number | number[]) => {
    const speed = Array.isArray(newValue) ? newValue[0] : newValue;
    onSpeedChange(motor.id, speed);
  };

  return (
    <Card
      sx={{
        minWidth: 300,
        opacity: disabled ? 0.6 : 1,
        transition: "opacity 0.3s ease",
      }}
    >
      <CardContent>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h6" component="h3">
            {motor.name}
          </Typography>
          <Chip
            label={`${motor.position}%`}
            color={motor.isMoving ? "primary" : "default"}
            size="small"
          />
        </Box>

        {/* Motor Control Buttons */}
        <Stack direction="row" spacing={1} mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={getMotorIcon()}
            onClick={handleLeftButtonClick}
            disabled={disabled || motor.isMoving}
            sx={{ flex: 1 }}
          >
            {motorConfig.left.label}
          </Button>

          <Button
            variant="contained"
            color="primary"
            startIcon={getMotorIcon()}
            onClick={handleRightButtonClick}
            disabled={disabled || motor.isMoving}
            sx={{ flex: 1 }}
          >
            {motorConfig.right.label}
          </Button>
        </Stack>

        {/* Stop Button */}
        <Button
          variant="outlined"
          color="error"
          startIcon={<Stop />}
          onClick={handleStopClick}
          disabled={disabled || !motor.isMoving}
          fullWidth
          sx={{ mb: 2 }}
        >
          Стоп
        </Button>

        {/* Speed Control */}
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Скорость: {motor.speed}
          </Typography>
          <Slider
            value={motor.speed}
            onChange={handleSpeedChange}
            min={50}
            max={255}
            step={5}
            disabled={disabled}
            marks={[
              { value: 50, label: "50" },
              { value: 150, label: "150" },
              { value: 255, label: "255" },
            ]}
            valueLabelDisplay="auto"
            sx={{ mb: 1 }}
          />
        </Box>

        {/* Status Indicator */}
        <Box display="flex" alignItems="center" justifyContent="center">
          <Chip
            icon={motor.isMoving ? <PlayArrow /> : <Stop />}
            label={motor.isMoving ? "Движется" : "Остановлен"}
            color={motor.isMoving ? "success" : "default"}
            size="small"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default MotorControl;
