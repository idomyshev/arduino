// WebSocket service for robot communication
import { WebSocketMessage, MotorCommand } from "../types/index.js";

export class RobotWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private onMessageCallback?: (message: WebSocketMessage) => void;
  private onConnectionChangeCallback?: (connected: boolean) => void;

  constructor() {
    this.connect();
  }

  private connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    console.log("Connecting to WebSocket:", wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventListeners();
    } catch (error) {
      console.error("Error creating WebSocket:", error);
      this.handleReconnect();
    }
  }

  private setupEventListeners() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log("WebSocket connected successfully");
      this.reconnectAttempts = 0;
      this.onConnectionChangeCallback?.(true);
      // Request current status
      this.send({ command: "get_status" });
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log("Received message:", data);
        this.onMessageCallback?.(data);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    this.ws.onclose = (event) => {
      console.log(
        "WebSocket disconnected. Code:",
        event.code,
        "Reason:",
        event.reason,
      );
      this.onConnectionChangeCallback?.(false);
      this.handleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
      );

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    } else {
      console.error("Max reconnection attempts reached");
    }
  }

  public send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  public connectToRobot() {
    this.send({ command: "connect" });
  }

  public disconnectFromRobot() {
    this.send({ command: "disconnect" });
  }

  public moveMotor(
    motor: number,
    direction: "forward" | "backward",
    speed: number,
    duration?: number,
  ) {
    const command: MotorCommand = {
      motor,
      direction,
      speed,
      duration,
    };

    this.send({
      command: "move_motor",
      ...command,
    });
  }

  public stopMotor(motor: number) {
    this.send({
      command: "stop_motor",
      motor,
    });
  }

  public stopAllMotors() {
    this.send({ command: "stop_all" });
  }

  public onMessage(callback: (message: WebSocketMessage) => void) {
    this.onMessageCallback = callback;
  }

  public onConnectionChange(callback: (connected: boolean) => void) {
    this.onConnectionChangeCallback = callback;
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
