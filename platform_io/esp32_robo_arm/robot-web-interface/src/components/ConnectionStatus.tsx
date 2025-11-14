// Connection Status Component
import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  Alert,
  CircularProgress,
} from "@mui/material";
import { Bluetooth, BluetoothDisabled } from "@mui/icons-material";

interface ConnectionStatusProps {
  connected: boolean;
  connecting: boolean;
  error?: string;
  onConnect: () => void;
  onDisconnect: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  connected,
  connecting,
  error,
  onConnect,
  onDisconnect,
}) => {
  const getStatusIcon = () => {
    if (connecting) return <CircularProgress size={20} />;
    return connected ? <Bluetooth /> : <BluetoothDisabled />;
  };

  const getStatusColor = () => {
    if (connecting) return "warning";
    return connected ? "success" : "error";
  };

  const getStatusText = () => {
    if (connecting) return "Подключение...";
    return connected ? "Подключено к роботу" : "Не подключено";
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h6" component="h2">
            🤖 Статус подключения
          </Typography>
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            color={getStatusColor() as any}
            variant={connected ? "filled" : "outlined"}
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            color="primary"
            onClick={onConnect}
            disabled={connecting || connected}
            startIcon={<Bluetooth />}
          >
            Подключиться
          </Button>

          <Button
            variant="outlined"
            color="error"
            onClick={onDisconnect}
            disabled={connecting || !connected}
            startIcon={<BluetoothDisabled />}
          >
            Отключиться
          </Button>
        </Box>

        {connected && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Робот готов к управлению! Используйте кнопки ниже для движения
            моторов.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ConnectionStatus;
