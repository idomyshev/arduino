// Main App Component
import React from "react";
import {
  Container,
  Typography,
  Box,
  Grid,
  AppBar,
  Toolbar,
  Button,
  Paper,
} from "@mui/material";
import { Settings, Stop, Home } from "@mui/icons-material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

import { useRobot } from "./hooks/useRobot";
import ConnectionStatus from "./components/ConnectionStatus";
import MotorControl from "./components/MotorControl";

// Create a custom theme
const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
    background: {
      default: "#0a0a0a",
      paper: "#1a1a1a",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const App: React.FC = () => {
  const {
    connection,
    motors,
    connectToRobot,
    disconnectFromRobot,
    moveMotor,
    stopMotor,
    stopAllMotors,
    updateMotorSpeed,
    isConnected,
  } = useRobot();

  const handleStopAll = () => {
    stopAllMotors();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          flexGrow: 1,
          minHeight: "100vh",
          backgroundColor: "background.default",
        }}
      >
        {/* App Bar */}
        <AppBar position="static" sx={{ backgroundColor: "primary.main" }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🤖 ESP32 Robot Arm Control
            </Typography>
            <Button color="inherit" startIcon={<Settings />} sx={{ mr: 1 }}>
              Настройки
            </Button>
            <Button
              color="inherit"
              startIcon={<Stop />}
              onClick={handleStopAll}
              disabled={!isConnected}
            >
              Стоп все
            </Button>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ py: 4 }}>
          {/* Header */}
          <Box textAlign="center" mb={4}>
            <Typography variant="h3" component="h1" gutterBottom>
              Управление роботом-рукой
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Современный веб-интерфейс для управления ESP32 роботом через
              Bluetooth
            </Typography>
          </Box>

          {/* Connection Status */}
          <ConnectionStatus
            connected={connection.connected}
            connecting={connection.connecting}
            error={connection.error}
            onConnect={connectToRobot}
            onDisconnect={disconnectFromRobot}
          />

          {/* Motor Controls */}
          <Paper sx={{ p: 3, backgroundColor: "background.paper" }}>
            <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
              🎮 Управление моторами
            </Typography>

            <Grid container spacing={3}>
              {motors.map((motor) => (
                <Grid item xs={12} md={4} key={motor.id}>
                  <MotorControl
                    motor={motor}
                    onMoveMotor={moveMotor}
                    onStopMotor={stopMotor}
                    onSpeedChange={updateMotorSpeed}
                    disabled={!connection.connected}
                  />
                </Grid>
              ))}
            </Grid>
          </Paper>

          {/* Footer */}
          <Box textAlign="center" mt={4}>
            <Typography variant="body2" color="text.secondary">
              ESP32 Robot Arm Control System v2.0
            </Typography>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;
