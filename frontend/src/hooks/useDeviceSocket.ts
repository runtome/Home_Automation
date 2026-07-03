import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { DEVICES_KEY } from "@/hooks/useDevices";
import { LOGS_KEY } from "@/hooks/useLogs";
import { Device, DeviceUpdateMessage } from "@/types/device";
import { WS_URL } from "@/utils/constants";
import { tokenStorage } from "@/utils/tokenStorage";

const INITIAL_RECONNECT_DELAY_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 15000;

export function useDeviceSocket(enabled: boolean) {
  const queryClient = useQueryClient();
  const reconnectDelayRef = useRef(INITIAL_RECONNECT_DELAY_MS);

  useEffect(() => {
    if (!enabled) return;

    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let closedByEffect = false;

    function connect() {
      const token = tokenStorage.getAccessToken();
      if (!token) return;

      socket = new WebSocket(`${WS_URL}/devices?token=${encodeURIComponent(token)}`);

      socket.onopen = () => {
        reconnectDelayRef.current = INITIAL_RECONNECT_DELAY_MS;
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as DeviceUpdateMessage;
          if (message.type === "device_update") {
            queryClient.setQueryData<Device[]>(DEVICES_KEY, (old) =>
              old
                ? old.some((d) => d.id === message.data.id)
                  ? old.map((d) => (d.id === message.data.id ? message.data : d))
                  : [...old, message.data]
                : old
            );
            queryClient.invalidateQueries({ queryKey: LOGS_KEY });
          }
        } catch {
          // ignore malformed frames
        }
      };

      socket.onclose = () => {
        if (closedByEffect) return;
        reconnectTimer = setTimeout(() => {
          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, MAX_RECONNECT_DELAY_MS);
          connect();
        }, reconnectDelayRef.current);
      };
    }

    connect();

    return () => {
      closedByEffect = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [enabled, queryClient]);
}
