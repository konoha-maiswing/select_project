import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

/**
 * 暗算力測定ツール
 * 外部ライブラリ不要。Java 17以上で動作します。
 */
public class AnzanBattle extends JFrame {
    private static final int QUESTION_COUNT = 15;
    private static final int POINTS_PER_CORRECT = 100;
    private static final Color BACKGROUND = new Color(21, 29, 45);
    private static final Color PANEL = new Color(33, 44, 65);
    private static final Color ACCENT = new Color(72, 157, 230);
    private static final Color TEXT = new Color(242, 246, 252);
    private static final Color MUTED = new Color(176, 190, 210);
    private static final Font NORMAL_FONT = new Font(Font.SANS_SERIF, Font.PLAIN, 16);
    private static final Font BOLD_FONT = new Font(Font.SANS_SERIF, Font.BOLD, 18);
    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final CardLayout cardLayout = new CardLayout();
    private final JPanel cards = new JPanel(cardLayout);
    private final Random random = new Random();
    private final Path dataDirectory = Path.of(System.getProperty("user.home"), ".anzan-battle");
    private final Path logFile = dataDirectory.resolve("records.csv");

    private JLabel todayStatusLabel;
    private JLabel questionNumberLabel;
    private JLabel questionLabel;
    private JLabel feedbackLabel;
    private JTextField answerField;
    private JButton answerButton;
    private JLabel resultCorrectLabel;
    private JLabel resultPowerLabel;
    private JLabel resultMessageLabel;

    private int questionIndex;
    private int correctCount;
    private int leftNumber;
    private int rightNumber;
    private boolean answered;
    private boolean recordEligible;

    public AnzanBattle() {
        super("暗算力測定ツール");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setMinimumSize(new Dimension(620, 520));
        setSize(760, 620);
        setLocationRelativeTo(null);
        getContentPane().setBackground(BACKGROUND);

        cards.setBackground(BACKGROUND);
        cards.add(createTitlePanel(), "title");
        cards.add(createGamePanel(), "game");
        cards.add(createResultPanel(), "result");
        cards.add(createLogPanel(), "log");
        setContentPane(cards);
        showTitle();
    }

    private JPanel createTitlePanel() {
        JPanel panel = basePanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new EmptyBorder(60, 70, 60, 70));

        JLabel title = label("暗算力測定", 38, true, TEXT);
        title.setAlignmentX(Component.CENTER_ALIGNMENT);
        JLabel subtitle = label("15問の2桁 × 2桁で、あなたの戦闘力を測定！", 16, false, MUTED);
        subtitle.setAlignmentX(Component.CENTER_ALIGNMENT);

        JButton startButton = primaryButton("スタート");
        startButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        startButton.addActionListener(e -> startGame());

        JButton logButton = secondaryButton("今日の記録・過去ログを見る");
        logButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        logButton.addActionListener(e -> showLogs());

        todayStatusLabel = label("", 14, false, MUTED);
        todayStatusLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        todayStatusLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JLabel rule = label("ルール：10〜99の掛け算を全15問。正解1問につき戦闘力 +100。", 13, false, MUTED);
        rule.setAlignmentX(Component.CENTER_ALIGNMENT);
        JLabel saveRule = label("<html><div style='text-align:center;'>1日に記録されるのは最初の1回分のみ。<br>2回目以降もプレイできますが、記録は追加されません。</div></html>", 13, false, MUTED);
        saveRule.setAlignmentX(Component.CENTER_ALIGNMENT);
        saveRule.setHorizontalAlignment(SwingConstants.CENTER);

        panel.add(Box.createVerticalGlue());
        panel.add(title);
        panel.add(Box.createVerticalStrut(12));
        panel.add(subtitle);
        panel.add(Box.createVerticalStrut(42));
        panel.add(startButton);
        panel.add(Box.createVerticalStrut(14));
        panel.add(logButton);
        panel.add(Box.createVerticalStrut(22));
        panel.add(todayStatusLabel);
        panel.add(Box.createVerticalStrut(28));
        panel.add(rule);
        panel.add(Box.createVerticalStrut(8));
        panel.add(saveRule);
        panel.add(Box.createVerticalGlue());
        return panel;
    }

    private JPanel createGamePanel() {
        JPanel panel = basePanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new EmptyBorder(55, 70, 55, 70));

        questionNumberLabel = label("第 1 問 / 15 問", 17, true, MUTED);
        questionNumberLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        questionLabel = label("00 × 00 = ?", 42, true, TEXT);
        questionLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        answerField = new JTextField();
        answerField.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 26));
        answerField.setHorizontalAlignment(JTextField.CENTER);
        answerField.setMaximumSize(new Dimension(300, 52));
        answerField.setPreferredSize(new Dimension(300, 52));
        answerField.addActionListener(e -> handleAnswerOrNext());

        feedbackLabel = label("答えを入力してください。", 16, false, MUTED);
        feedbackLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        feedbackLabel.setHorizontalAlignment(SwingConstants.CENTER);

        answerButton = primaryButton("回答する");
        answerButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        answerButton.addActionListener(e -> handleAnswerOrNext());

        JLabel hint = label("Enterキーでも回答・次の問題への移動ができます。", 13, false, MUTED);
        hint.setAlignmentX(Component.CENTER_ALIGNMENT);

        panel.add(Box.createVerticalGlue());
        panel.add(questionNumberLabel);
        panel.add(Box.createVerticalStrut(28));
        panel.add(questionLabel);
        panel.add(Box.createVerticalStrut(32));
        panel.add(answerField);
        panel.add(Box.createVerticalStrut(18));
        panel.add(feedbackLabel);
        panel.add(Box.createVerticalStrut(20));
        panel.add(answerButton);
        panel.add(Box.createVerticalStrut(16));
        panel.add(hint);
        panel.add(Box.createVerticalGlue());
        return panel;
    }

    private JPanel createResultPanel() {
        JPanel panel = basePanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new EmptyBorder(60, 70, 60, 70));

        JLabel title = label("測定結果", 34, true, TEXT);
        title.setAlignmentX(Component.CENTER_ALIGNMENT);
        resultCorrectLabel = label("正解数：0 / 15", 24, true, TEXT);
        resultCorrectLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        resultPowerLabel = label("あなたの戦闘力：0", 30, true, new Color(255, 209, 102));
        resultPowerLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        resultMessageLabel = label("", 15, false, MUTED);
        resultMessageLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        resultMessageLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JButton titleButton = primaryButton("タイトルへ戻る");
        titleButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        titleButton.addActionListener(e -> showTitle());

        panel.add(Box.createVerticalGlue());
        panel.add(title);
        panel.add(Box.createVerticalStrut(36));
        panel.add(resultCorrectLabel);
        panel.add(Box.createVerticalStrut(18));
        panel.add(resultPowerLabel);
        panel.add(Box.createVerticalStrut(30));
        panel.add(resultMessageLabel);
        panel.add(Box.createVerticalStrut(36));
        panel.add(titleButton);
        panel.add(Box.createVerticalGlue());
        return panel;
    }

    private JPanel createLogPanel() {
        JPanel panel = basePanel();
        panel.setLayout(new BorderLayout(12, 18));
        panel.setBorder(new EmptyBorder(32, 42, 32, 42));
        panel.setName("log");

        JLabel title = label("挑戦ログ", 30, true, TEXT);
        title.setHorizontalAlignment(SwingConstants.CENTER);
        panel.add(title, BorderLayout.NORTH);

        String[] columns = {"日付", "正解数", "戦闘力", "記録日時"};
        DefaultTableModel model = new DefaultTableModel(columns, 0) {
            @Override public boolean isCellEditable(int row, int column) { return false; }
        };
        JTable table = new JTable(model);
        table.setFont(NORMAL_FONT);
        table.setRowHeight(30);
        table.getTableHeader().setFont(BOLD_FONT);
        table.setFillsViewportHeight(true);
        JScrollPane scrollPane = new JScrollPane(table);
        panel.add(scrollPane, BorderLayout.CENTER);

        JButton backButton = secondaryButton("タイトルへ戻る");
        backButton.addActionListener(e -> showTitle());
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.CENTER));
        bottom.setOpaque(false);
        bottom.add(backButton);
        panel.add(bottom, BorderLayout.SOUTH);

        // ログ表示のたびに最新データを読み込むため、テーブルモデルを保持する。
        table.putClientProperty("logModel", model);
        return panel;
    }

    private JPanel basePanel() {
        JPanel panel = new JPanel();
        panel.setBackground(BACKGROUND);
        return panel;
    }

    private JLabel label(String text, int size, boolean bold, Color color) {
        JLabel label = new JLabel(text);
        label.setFont(new Font(Font.SANS_SERIF, bold ? Font.BOLD : Font.PLAIN, size));
        label.setForeground(color);
        return label;
    }

    private JButton primaryButton(String text) {
        JButton button = new JButton(text);
        button.setFont(BOLD_FONT);
        button.setForeground(Color.WHITE);
        button.setBackground(ACCENT);
        button.setFocusPainted(false);
        button.setBorder(new EmptyBorder(12, 30, 12, 30));
        button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        button.setAlignmentX(Component.CENTER_ALIGNMENT);
        return button;
    }

    private JButton secondaryButton(String text) {
        JButton button = new JButton(text);
        button.setFont(NORMAL_FONT);
        button.setForeground(TEXT);
        button.setBackground(PANEL);
        button.setFocusPainted(false);
        button.setBorder(new EmptyBorder(10, 22, 10, 22));
        button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        button.setAlignmentX(Component.CENTER_ALIGNMENT);
        return button;
    }

    private void showTitle() {
        updateTodayStatus();
        cardLayout.show(cards, "title");
    }

    private void updateTodayStatus() {
        if (todayStatusLabel == null) return;
        LocalDate today = LocalDate.now();
        List<ChallengeRecord> records = readRecords();
        ChallengeRecord todaysRecord = records.stream()
                .filter(record -> record.date.equals(today))
                .findFirst().orElse(null);
        if (todaysRecord == null) {
            todayStatusLabel.setText("今日はまだ記録がありません。最初の挑戦が記録対象です。");
        } else {
            todayStatusLabel.setText("本日の記録：正解 " + todaysRecord.correct + "/" + QUESTION_COUNT
                    + "問 ／ 戦闘力 " + todaysRecord.power + "（再挑戦分は記録されません）");
        }
    }

    private void startGame() {
        // 完了済みの本日ログがある場合、今回はプレイできるが保存対象外。
        recordEligible = readRecords().stream().noneMatch(record -> record.date.equals(LocalDate.now()));
        questionIndex = 0;
        correctCount = 0;
        showQuestion();
        cardLayout.show(cards, "game");
    }

    private void showQuestion() {
        leftNumber = random.nextInt(90) + 10;
        rightNumber = random.nextInt(90) + 10;
        answered = false;
        questionNumberLabel.setText("第 " + (questionIndex + 1) + " 問 / " + QUESTION_COUNT + " 問");
        questionLabel.setText(leftNumber + " × " + rightNumber + " = ?");
        feedbackLabel.setText("答えを入力してください。");
        feedbackLabel.setForeground(MUTED);
        answerField.setText("");
        answerField.setEnabled(true);
        answerButton.setText("回答する");
        answerField.requestFocusInWindow();
    }

    private void handleAnswerOrNext() {
        if (!answered) {
            submitAnswer();
        } else {
            goToNextQuestion();
        }
    }

    private void submitAnswer() {
        String input = answerField.getText().trim();
        final int userAnswer;
        try {
            if (input.isEmpty()) throw new NumberFormatException();
            userAnswer = Integer.parseInt(input);
        } catch (NumberFormatException ex) {
            feedbackLabel.setText("数字で答えを入力してください。");
            feedbackLabel.setForeground(new Color(255, 160, 140));
            return;
        }

        int correctAnswer = leftNumber * rightNumber;
        answered = true;
        answerField.setEnabled(false);
        if (userAnswer == correctAnswer) {
            correctCount++;
            feedbackLabel.setText("正解！");
            feedbackLabel.setForeground(new Color(115, 220, 160));
        } else {
            feedbackLabel.setText("不正解。正解は " + correctAnswer + " です。");
            feedbackLabel.setForeground(new Color(255, 160, 140));
        }
        answerButton.setText(questionIndex == QUESTION_COUNT - 1 ? "結果を見る" : "次の問題へ");
    }

    private void goToNextQuestion() {
        if (questionIndex < QUESTION_COUNT - 1) {
            questionIndex++;
            showQuestion();
        } else {
            finishGame();
        }
    }

    private void finishGame() {
        int power = correctCount * POINTS_PER_CORRECT;
        resultCorrectLabel.setText("正解数：" + correctCount + " / " + QUESTION_COUNT);
        resultPowerLabel.setText("あなたの戦闘力：" + power);

        boolean saved = false;
        String message;
        if (recordEligible) {
            try {
                saved = saveRecordIfAbsent(new ChallengeRecord(LocalDate.now(), correctCount, power,
                        LocalDateTime.now().format(TIME_FORMAT)));
                message = saved
                        ? "本日の記録として保存しました。"
                        : "本日の記録は既にあるため、今回は保存されませんでした。";
            } catch (IOException ex) {
                message = "ログの保存に失敗しました：" + ex.getMessage();
            }
        } else {
            message = "本日の記録は既に保存済みのため、今回は記録されません。\nプレイ結果は確認できます。";
        }
        resultMessageLabel.setText("<html><div style='text-align:center;'>" + message.replace("\n", "<br>") + "</div></html>");
        cardLayout.show(cards, "result");
    }

    private void showLogs() {
        Component logPanel = findPanel("log");
        if (logPanel instanceof JPanel panel) {
            JTable table = findTable(panel);
            if (table != null && table.getModel() instanceof DefaultTableModel model) {
                model.setRowCount(0);
                List<ChallengeRecord> records = readRecords();
                records.sort(Comparator.comparing((ChallengeRecord r) -> r.date).reversed());
                for (ChallengeRecord record : records) {
                    model.addRow(new Object[]{record.date.toString(), record.correct + " / " + QUESTION_COUNT,
                            record.power, record.recordedAt});
                }
            }
        }
        cardLayout.show(cards, "log");
    }

    private Component findPanel(String name) {
        for (Component component : cards.getComponents()) {
            if (component.getName() != null && component.getName().equals(name)) return component;
        }
        // CardLayoutで追加した順番：title, game, result, log
        return cards.getComponent(3);
    }

    private JTable findTable(Container container) {
        for (Component component : container.getComponents()) {
            if (component instanceof JScrollPane scrollPane
                    && scrollPane.getViewport().getView() instanceof JTable table) return table;
            if (component instanceof Container child) {
                JTable found = findTable(child);
                if (found != null) return found;
            }
        }
        return null;
    }

    private List<ChallengeRecord> readRecords() {
        List<ChallengeRecord> records = new ArrayList<>();
        if (!Files.exists(logFile)) return records;
        try {
            for (String line : Files.readAllLines(logFile, StandardCharsets.UTF_8)) {
                if (line.isBlank() || line.startsWith("date,")) continue;
                String[] parts = line.split(",", 4);
                if (parts.length != 4) continue;
                try {
                    records.add(new ChallengeRecord(LocalDate.parse(parts[0]), Integer.parseInt(parts[1]),
                            Integer.parseInt(parts[2]), parts[3]));
                } catch (RuntimeException ignored) {
                    // 壊れた行があっても、他のログは表示する。
                }
            }
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this, "ログを読み込めませんでした：" + ex.getMessage(),
                    "読み込みエラー", JOptionPane.WARNING_MESSAGE);
        }
        return records;
    }

    private boolean saveRecordIfAbsent(ChallengeRecord record) throws IOException {
        Files.createDirectories(dataDirectory);
        // 保存直前にも確認し、同じ日の重複記録を防止する。
        boolean alreadySaved = readRecords().stream().anyMatch(existing -> existing.date.equals(record.date));
        if (alreadySaved) return false;
        boolean newFile = !Files.exists(logFile);
        StringBuilder content = new StringBuilder();
        if (newFile) content.append("date,correct,power,recorded_at\n");
        content.append(record.date).append(',').append(record.correct).append(',')
                .append(record.power).append(',').append(record.recordedAt).append('\n');
        Files.writeString(logFile, content.toString(), StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        return true;
    }

    private static class ChallengeRecord {
        final LocalDate date;
        final int correct;
        final int power;
        final String recordedAt;

        ChallengeRecord(LocalDate date, int correct, int power, String recordedAt) {
            this.date = date;
            this.correct = correct;
            this.power = power;
            this.recordedAt = recordedAt;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) { }
            new AnzanBattle().setVisible(true);
        });
    }
}
