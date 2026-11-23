import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDate;
import java.util.*;
import java.util.List;

public class MentalMathPower extends JFrame {

    private static final int TOTAL_QUESTIONS = 15;
    private static final int POINTS_PER_QUESTION = 1000; // 1問正解 = 戦闘力1000
    private static final Path LOG_FILE = Paths.get("mental_math_log.csv");

    private final CardLayout cards = new CardLayout();
    private final JPanel root = new JPanel(cards);

    // タイトル画面
    private final JLabel titleNotice = new JLabel(" ", SwingConstants.CENTER);

    // 問題画面
    private final JLabel progressLabel = new JLabel("", SwingConstants.CENTER);
    private final JLabel questionLabel = new JLabel("", SwingConstants.CENTER);
    private final JLabel practiceLabel = new JLabel(" ", SwingConstants.CENTER);
    private final JLabel feedbackLabel = new JLabel(" ", SwingConstants.CENTER);
    private final JTextField answerField = new JTextField();
    private final JButton answerButton = new JButton("回答");

    // 結果画面
    private final JLabel resultLabel = new JLabel("", SwingConstants.CENTER);
    private final JLabel resultNotice = new JLabel("", SwingConstants.CENTER);

    // ログ画面
    private final JTextArea logArea = new JTextArea();

    private final Random random = new Random();
    private int a, b, questionNo, correctCount;
    private boolean recordable; // 今回の挑戦が記録対象か
    private boolean waitingNext; // 正誤表示後、次へ進む待ち状態

    public MentalMathPower() {
        super("暗算力測定ツール");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(480, 360);
        setLocationRelativeTo(null);

        root.add(buildTitlePanel(), "title");
        root.add(buildQuestionPanel(), "question");
        root.add(buildResultPanel(), "result");
        root.add(buildLogPanel(), "log");
        add(root);
        showTitle();
    }

    // ---------- 画面構築 ----------
    private JPanel buildTitlePanel() {
        JPanel p = new JPanel(new GridLayout(0, 1, 10, 10));
        p.setBorder(BorderFactory.createEmptyBorder(30, 60, 30, 60));
        JLabel title = new JLabel("暗算戦闘力測定", SwingConstants.CENTER);
        title.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 28));
        JButton start = new JButton("スタート");
        start.addActionListener(e -> startChallenge());
        JButton log = new JButton("ログを見る");
        log.addActionListener(e -> showLog());
        p.add(title);
        p.add(titleNotice);
        p.add(start);
        p.add(log);
        return p;
    }

    private JPanel buildQuestionPanel() {
        JPanel p = new JPanel(new GridLayout(0, 1, 8, 8));
        p.setBorder(BorderFactory.createEmptyBorder(20, 60, 20, 60));
        questionLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 36));
        answerField.setHorizontalAlignment(JTextField.CENTER);
        answerField.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 24));
        feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 18));
        practiceLabel.setForeground(Color.RED.darker());
        answerButton.addActionListener(e -> onAnswer());
        answerField.addActionListener(e -> onAnswer());
        p.add(progressLabel);
        p.add(practiceLabel);
        p.add(questionLabel);
        p.add(answerField);
        p.add(answerButton);
        p.add(feedbackLabel);
        return p;
    }

    private JPanel buildResultPanel() {
        JPanel p = new JPanel(new GridLayout(0, 1, 10, 10));
        p.setBorder(BorderFactory.createEmptyBorder(30, 40, 30, 40));
        resultLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 22));
        JButton back = new JButton("タイトルへ戻る");
        back.addActionListener(e -> showTitle());
        p.add(resultLabel);
        p.add(resultNotice);
        p.add(back);
        return p;
    }

    private JPanel buildLogPanel() {
        JPanel p = new JPanel(new BorderLayout(8, 8));
        p.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        logArea.setEditable(false);
        logArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 14));
        JButton back = new JButton("タイトルへ戻る");
        back.addActionListener(e -> showTitle());
        p.add(new JLabel("これまでの記録"), BorderLayout.NORTH);
        p.add(new JScrollPane(logArea), BorderLayout.CENTER);
        p.add(back, BorderLayout.SOUTH);
        return p;
    }

    // ---------- 画面遷移 ----------
    private void showTitle() {
        if (hasPlayedToday()) {
            titleNotice.setText("<html><center>本日は挑戦済みです。<br>今日の2回目以降は練習扱いで記録されません。</center></html>");
        } else {
            titleNotice.setText("今日はまだ挑戦していません（1日1回のみ記録）");
        }
        cards.show(root, "title");
    }

    private void showLog() {
        List<String> lines = readLog();
        StringBuilder sb = new StringBuilder();
        if (lines.isEmpty()) {
            sb.append("まだ記録がありません。");
        } else {
            sb.append(String.format("%-12s %-6s %s%n", "日付", "正解", "戦闘力"));
            sb.append("------------------------------\n");
            for (String line : lines) {
                String[] t = line.split(",");
                if (t.length < 3) continue;
                sb.append(String.format("%-12s %2s/%-3d %s%n", t[0], t[1], TOTAL_QUESTIONS, t[2]));
            }
        }
        logArea.setText(sb.toString());
        logArea.setCaretPosition(0);
        cards.show(root, "log");
    }

    // ---------- ゲーム進行 ----------
    private void startChallenge() {
        recordable = !hasPlayedToday();
        questionNo = 0;
        correctCount = 0;
        practiceLabel.setText(recordable ? " " : "※ 本日2回目以降のため、この結果は記録されません");
        cards.show(root, "question");
        nextQuestion();
    }

    private void nextQuestion() {
        questionNo++;
        a = 10 + random.nextInt(90);
        b = 10 + random.nextInt(90);
        progressLabel.setText("第 " + questionNo + " 問 / " + TOTAL_QUESTIONS);
        questionLabel.setText(a + " × " + b + " = ?");
        feedbackLabel.setText(" ");
        answerField.setText("");
        answerField.setEnabled(true);
        answerButton.setText("回答");
        waitingNext = false;
        answerField.requestFocusInWindow();
    }

    private void onAnswer() {
        // 正誤表示後は「次へ」として動作
        if (waitingNext) {
            if (questionNo >= TOTAL_QUESTIONS) {
                finish();
            } else {
                nextQuestion();
            }
            return;
        }
        String text = answerField.getText().trim();
        int value;
        try {
            value = Integer.parseInt(text);
        } catch (NumberFormatException ex) {
            feedbackLabel.setForeground(Color.GRAY);
            feedbackLabel.setText("数字を入力してください");
            return;
        }
        if (value == a * b) {
            correctCount++;
            feedbackLabel.setForeground(new Color(0, 140, 0));
            feedbackLabel.setText("正解！");
        } else {
            feedbackLabel.setForeground(Color.RED);
            feedbackLabel.setText("不正解… 正解は " + (a * b));
        }
        answerField.setEnabled(false);
        waitingNext = true;
        answerButton.setText(questionNo >= TOTAL_QUESTIONS ? "結果を見る" : "次の問題へ");
        answerButton.requestFocusInWindow();
    }

    private void finish() {
        int power = correctCount * POINTS_PER_QUESTION;
        resultLabel.setText("<html><center>正解数: " + correctCount + " / " + TOTAL_QUESTIONS
                + "<br>あなたの暗算戦闘力: " + power + "</center></html>");
        if (recordable) {
            appendLog(correctCount, power);
            resultNotice.setText("今日の記録として保存しました。");
        } else {
            resultNotice.setText("<html><center>本日2回目以降の挑戦のため、<br>この結果は記録されません。</center></html>");
        }
        cards.show(root, "result");
    }

    // ---------- ログ処理 ----------
    private boolean hasPlayedToday() {
        String today = LocalDate.now().toString();
        for (String line : readLog()) {
            if (line.startsWith(today + ",")) return true;
        }
        return false;
    }

    private List<String> readLog() {
        try {
            if (Files.exists(LOG_FILE)) {
                List<String> lines = new ArrayList<>(Files.readAllLines(LOG_FILE, StandardCharsets.UTF_8));
                lines.removeIf(String::isBlank);
                return lines;
            }
        } catch (IOException e) {
            JOptionPane.showMessageDialog(this, "ログの読み込みに失敗しました: " + e.getMessage());
        }
        return new ArrayList<>();
    }

    private void appendLog(int correct, int power) {
        String line = LocalDate.now() + "," + correct + "," + power + System.lineSeparator();
        try {
            Files.write(LOG_FILE, line.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            JOptionPane.showMessageDialog(this, "ログの保存に失敗しました: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new MentalMathPower().setVisible(true));
    }
}
