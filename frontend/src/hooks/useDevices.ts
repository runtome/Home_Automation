import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { deviceService } from "@/services/deviceService";
import { Device } from "@/types/device";

const DEVICES_KEY = ["devices"];

export function useDevices() {
  return useQuery({
    queryKey: DEVICES_KEY,
    queryFn: deviceService.list,
    refetchInterval: 30_000, // fallback in case the websocket connection drops
  });
}

function useRelayMutation(action: (id: number) => Promise<Device>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: action,
    onSuccess: (updated) => {
      queryClient.setQueryData<Device[]>(DEVICES_KEY, (old) =>
        old ? old.map((d) => (d.id === updated.id ? updated : d)) : old
      );
    },
  });
}

export function useTurnOn() {
  return useRelayMutation(deviceService.turnOn);
}

export function useTurnOff() {
  return useRelayMutation(deviceService.turnOff);
}

export function useToggle() {
  return useRelayMutation(deviceService.toggle);
}

export { DEVICES_KEY };
