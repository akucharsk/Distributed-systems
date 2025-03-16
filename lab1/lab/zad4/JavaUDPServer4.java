package zad4;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUDPServer4 {
    public static void main(String[] args) {
        DatagramSocket socket = null;
        final int portNumber = args.length > 0 ? Integer.parseInt(args[0]) : 8008;
        final String host = args.length > 1 ? args[1] : "localhost";

        try {
            socket = new DatagramSocket(portNumber, InetAddress.getByName(host));
            byte[] buffer = new byte[1024];

            while (true) {
                Arrays.fill(buffer, (byte) 0);
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                String message = new String(packet.getData());
                InetAddress clientAddress = packet.getAddress();
                int clientPort = packet.getPort();
                String openingMsg = message.charAt(0) == 'J' ?
                        "Received from Java client" : "Received from Python client";

                System.out.printf("%s %s:%d\n  %s", openingMsg, clientAddress.getHostAddress(),
                        clientPort, message.substring(1));
                String response = message.charAt(0) == 'J' ? "Java Pong" : "Python Pong";
                DatagramPacket respPacket = new DatagramPacket(response.getBytes(), response.length(),
                        clientAddress, clientPort);
                socket.send(respPacket);
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
