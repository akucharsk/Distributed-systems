package zad1;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUDPServer1 {
    public static void main(String[] args) {
        final int port = args.length > 0 ? Integer.parseInt(args[0]) : 8008;
        DatagramSocket socket = null;
        final String host = "127.0.0.1";


        final int bufferSize = 1024;
        try {
            socket = new DatagramSocket(port, InetAddress.getByName(host));
            byte[] buffer = new byte[bufferSize];

            while (true) {
                Arrays.fill(buffer, (byte) 0);
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                String clientMsg = new String(packet.getData());

                if (clientMsg.startsWith("kill")) {
                    System.out.println("User requested my death");
                    break;
                }
                InetAddress clientAddress = packet.getAddress();
                int clientPort = packet.getPort();
                System.out.printf("Client: %s:%d sends:\n%s\n\n", clientAddress.getHostAddress(), clientPort, new String(packet.getData()));

                StringBuilder messageBuilder = new StringBuilder();
                String message = messageBuilder
                        .append("Dear client ")
                        .append(clientAddress.getHostAddress())
                        .append(':')
                        .append(clientPort)
                        .append('.')
                        .append(" Please stop sending such idiotic nonsense, thank you!")
                        .toString();
                DatagramPacket sendPacket = new DatagramPacket(message.getBytes(), message.getBytes().length, clientAddress, clientPort);
                socket.send(sendPacket);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}
