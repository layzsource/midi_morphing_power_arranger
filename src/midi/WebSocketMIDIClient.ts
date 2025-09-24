/**
 * WebSocket MIDI Client
 * Connects to Python MIDI bridge for real-time MIDI data
 */

export interface MIDIMessage {
    type: 'cc' | 'note_on' | 'note_off';
    channel: number;
    timestamp: number;

    // CC-specific
    cc?: number;
    value?: number;
    normalized?: number;

    // Note-specific
    note?: number;
    velocity?: number;
    normalized_velocity?: number;
}

export class WebSocketMIDIClient {
    private ws: WebSocket | null = null;
    private reconnectInterval: number = 1000;
    private maxReconnectAttempts: number = 10;
    private reconnectAttempts: number = 0;
    private isConnected: boolean = false;
    private eventHandlers: Map<string, Function[]> = new Map();

    constructor(private url: string = 'ws://localhost:8765') {
        this.setupEventHandlers();
    }

    private setupEventHandlers() {
        this.eventHandlers.set('cc', []);
        this.eventHandlers.set('note_on', []);
        this.eventHandlers.set('note_off', []);
        this.eventHandlers.set('connected', []);
        this.eventHandlers.set('disconnected', []);
        this.eventHandlers.set('error', []);
    }

    public on(event: string, handler: Function) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event)!.push(handler);
    }

    public off(event: string, handler: Function) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    private emit(event: string, data?: any) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.forEach(handler => handler(data));
        }
    }

    public connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.warn('WebSocket already connected');
            return;
        }

        console.log(`Connecting to MIDI Bridge at ${this.url}`);

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = (event) => {
                console.log('✓ Connected to MIDI Bridge');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const message: MIDIMessage = JSON.parse(event.data);
                    this.handleMIDIMessage(message);
                } catch (error) {
                    console.error('Failed to parse MIDI message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('MIDI Bridge connection closed');
                this.isConnected = false;
                this.emit('disconnected');

                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        console.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                        this.connect();
                    }, this.reconnectInterval);
                }
            };

            this.ws.onerror = (error) => {
                console.error('MIDI Bridge WebSocket error:', error);
                this.emit('error', error);
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.emit('error', error);
        }
    }

    private handleMIDIMessage(message: MIDIMessage) {
        // Debug logging
        if (message.type === 'cc') {
            console.log(`WebSocket MIDI CC${message.cc}: ${message.value} (${message.normalized?.toFixed(3)})`);
        } else if (message.type === 'note_on') {
            console.log(`WebSocket MIDI Note On: ${message.note} velocity ${message.velocity}`);
        } else if (message.type === 'note_off') {
            console.log(`WebSocket MIDI Note Off: ${message.note}`);
        }

        // Emit to specific handlers
        this.emit(message.type, message);
    }

    public disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }

    public getConnectionStatus(): boolean {
        return this.isConnected;
    }
}

// Global instance
export const webSocketMIDI = new WebSocketMIDIClient();