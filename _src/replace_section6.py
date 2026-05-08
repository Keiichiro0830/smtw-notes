"""Replace Section 6 with the detailed version recovered from the decrypted 260411 page."""
from pathlib import Path

base = Path(r"C:\Users\keima\OneDrive\Documents\Work\40 Still Modelling The World (SMTW)\_src")
src = base / "Kawaguchi_seminar.html"

text = src.read_text(encoding="utf-8")

# Find boundaries
start_marker = '    <h2 id="sec6">'
end_marker = '    <footer>参加者限定 ／ 転載禁止 ／ 著作権は各論文の権利者に帰属</footer>'

i = text.find(start_marker)
j = text.find(end_marker)
assert i != -1 and j != -1, f"markers not found: {i}, {j}"

new_section = '''    <h2 id="sec6">6. 第1回ミーティング 議事メモ（2026-04-11）</h2>
    <p style="color:#64748b;font-size:0.9rem;">2026年4月11日（土）10:30〜12:15 JST ／ 早稲田大学 ／ 事前読了資料: <a href="https://www.boj.or.jp/about/press/koen_2025/data/ko251020a1.pdf" target="_blank" rel="noopener">高田日銀政策委員 講演録 (PDF)</a></p>

    <div class="participants-box">
        <h3 style="margin-top:0;color:#2c5282;">参加者</h3>
        <ul>
            <li><strong>川口先生</strong> — 早稲田大学 元教授・不動産金融工学</li>
            <li><strong>松前 景一郎</strong> — アドミン・司会進行</li>
            <li><strong>飯沼先生</strong> — SBI新生銀行・市場リスク担当、川口先生の授業「金融と資産金融工学」を引き継ぎ講義担当</li>
            <li><strong>黒田先生</strong> — 大学教員、ミクロ経済学の実証が専門</li>
            <li><strong>佐々木 Kazui</strong> — 公認会計士、川口先生のゼミ生（2年前）</li>
            <li><strong>鈴木 康太</strong> — 三井住友トラスト基礎研究所、不動産の調査分析・私募REIT/私募ファンドの投資助言業</li>
            <li><strong>淺川</strong> — ドイツ印刷機メーカー・財務経理、ゼミの演習で川口先生に師事</li>
            <li><strong>鈴木</strong> — 不動産業界勤務、外部マネージャーのデューデリジェンス等</li>
            <li><strong>宮武</strong> — WBS新M2、自営業・元PEファンド独立、バリューアップコンサル</li>
        </ul>
    </div>

    <h3 style="color:#1f3a5f;margin-top:1.4rem;">6.1 開会・趣旨説明（松前 景一郎）</h3>
    <p>川口先生の定年退職後も知的交流を続けるため、少人数のディスカッショングループを組成した経緯を共有。</p>
    <ul>
        <li>並行して Facebook グループと DMM オンラインサロン（月額550円）も運営中。DMM は講義ビデオ・資料のアップロード先として、炎上リスクのないクローズドな有料プラットフォームとして選定。</li>
        <li>目標は <strong>1年間の月次ディスカッション</strong>を通じて、最終的に<strong>出版物</strong>としてまとめること。</li>
        <li>録画・録音の許可を参加者に依頼。参加者の顔や発言がそのままインターネットに公開されることはない。</li>
        <li>将来的には、川口先生の映像・音声データから AI で再現コンテンツを作成する可能性も検討中。</li>
        <li>メンバーの人数はディスカッションの熱量を維持するために限定的にコントロールする方針。</li>
    </ul>

    <div class="speaker-block">
        <h4 class="sb-name">川口先生からの補足</h4>
        <ul>
            <li>退職後はバーチャルな場で知的交流を維持したい。早稲田に研究室がなくなったので、まずはバーチャルで。</li>
            <li>Facebook は「立ち食いそば」的な情報共有の場で、対話は別途必要。</li>
            <li>DMM サロンは現在参加者11名。メルマガで日経記事の AI コメントを実験的に開始。</li>
            <li>不動産 ST の業界裏話など、公開 SNS では議論しにくい内容がある。</li>
        </ul>
    </div>

    <h3 style="color:#1f3a5f;margin-top:1.4rem;">6.2 参加者自己紹介と AI に関する議論</h3>

    <div class="speaker-block">
        <h4 class="sb-name">飯沼先生（SBI新生銀行）</h4>
        <ul>
            <li>企業では Teams と Copilot による議事録作成が一般化。若手が「デッチ奉公」的トレーニングを経ずに育つ懸念。</li>
            <li>AI の精度は8割程度で、最終チェックは人間が必要。</li>
            <li>人間の目を育てる観点が抜け落ちている。</li>
            <li>道元の「只管打坐 (しかんたざ)」（手を使うことで理解する）の考え方に共感。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">黒田先生（大学教員）</h4>
        <ul>
            <li>現時点では AI でプロレベルのアウトプットは出ない（論文は正直話にならない）。</li>
            <li>ただし数年で、トップ数パーセント以外はほとんど代替される可能性。</li>
            <li>学生間の AI リテラシー格差が拡大中。AI は能力の増幅装置。</li>
            <li>早稲田はまだ良いが、他の大学ではマクロ的に格差が開く懸念。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">佐々木 Kazui（公認会計士）</h4>
        <ul>
            <li>川口先生の考え方（日本のビジネスは非協力ゲームではなく協力ゲームではないかという視点）に魅力を感じ参加。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">鈴木 康太（三井住友トラスト基礎研究所）</h4>
        <ul>
            <li>AI は能力のレバレッジ。元の能力が小さければアウトプットは限定的。</li>
            <li>農作業 → IT → AI と進むにつれ個人差は拡大。二極化は基本的に進む。</li>
            <li>AI 時代に知的鍛錬法はまさに求められるもの。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">淺川</h4>
        <ul>
            <li>職場でも Copilot 利用が広がるが、大学院経験者と年配者でレベル差がある。</li>
            <li>資本主義的に、トップ層・AI 活用層・非活用層の3層に分かれるのではないか。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">鈴木（不動産業界）</h4>
        <ul>
            <li>リサーチの入口として AI が有用。SEC の公開情報から PDF の該当ページまでピンポイントでピックアップしてくれる。</li>
            <li>英語で数十〜数百ページある資料を端的にピックアップする能力は純粋に役立っている。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">宮武（WBS M2）</h4>
        <ul>
            <li>PE ファンドから独立してバリューアップのコンサルをしているが、新しいビジネスを作りたい。</li>
            <li>Claude Code で論文の再現分析を自動で回す取り組みを開始。Journal of Finance 等の論文を日本市場データで再現。</li>
            <li>月100件の総当たりも可能。パワーを実感。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">川口先生の AI 観</h4>
        <ul>
            <li>ハーバート・サイモンは「知能とは記号システムの働き」と言ったが、1980 年代のエキスパートシステムは実用にならなかった。</li>
            <li>今の生成 AI は記号システムではなく <strong>数値システム</strong>。確率計算で最もらしい単語をつなげる。</li>
            <li><strong>背後に思考はなく知性もない</strong>。人間が認知を投影して思考があると錯覚する。この「錯覚を利用した」のが ChatGPT のすごさ。</li>
            <li>AI は「<strong>検索機能 ＋ 独り言</strong>」。検索と要約は有用。</li>
            <li>AI バブル: 2000 円の Claude でレポートを書いて 100 万〜1000 万円で売れる。情報の非対称性がなくなった途端にバブル崩壊。</li>
        </ul>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">松前 景一郎の所感</h4>
        <ul>
            <li>ホワイトカラーのエキスパタイズが AI に取られる中で、政治的不安定が生まれる可能性。</li>
            <li>「グッドクエスチョン」を見つける力が重要。</li>
            <li>AI に悪い倫理観が組み込まれた場合、人間は抗えなくなるかもしれない。真善美を問う力が重要。</li>
        </ul>
    </div>

    <h3 style="color:#1f3a5f;margin-top:1.4rem;">6.3 日本経済とバブル論争</h3>
    <p>川口先生が、日銀政策委員・高田氏の<a href="https://www.boj.or.jp/about/press/koen_2025/data/ko251020a1.pdf" target="_blank" rel="noopener">講演録</a>を題材として提示。事前に Claude で要約・反論を整理して共有済み。</p>

    <h4 style="color:#2c5282;margin-top:1rem;">高田レポートの要旨</h4>
    <ul>
        <li>高田氏は「バブルではなく構造変化」と主張。</li>
        <li>企業収益は 2004 年頃から急拡大。労働分配率は上がっておらず、賃金は抑制。</li>
        <li>実質金利がマイナスで、G7 の中でも日本は突出。</li>
    </ul>

    <h4 style="color:#2c5282;margin-top:1rem;">テーマ: バブルか構造変化か？</h4>

    <div class="speaker-block">
        <h4 class="sb-name">松前 景一郎</h4>
        <p>構造変化とバブルが同時並行で起きている可能性を否定しきれない。体感的にはバブルだが、不動産価格も高すぎるのではないか。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">鈴木 康太</h4>
        <p>個人的にはバブルの気配はあるが、長期で見ると株と不動産価格はまだ上がると考えている。イギリスからアメリカへの覇権移動と同じ構造。ただし短期的にはバブルの兆候もあり（広尾ガーデンヒルズが 8 億で売り出して 6 億）。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">宮武</h4>
        <p>名目値ベースではバブルではない。PER や TBR 等の指標は平成バブルのような異常値にはなっていない。ただし実質ベースとの乖離が拡大。労働分配率の低さが構造的問題。「株高不況」の指摘もある。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">飯沼先生</h4>
        <p>労働分配率が上がらないのは、バブルを経験した経営者のマインド。分配率上昇には相当時間がかかる。構造変化しながらこの状況が続くのではないか。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">淺川</h4>
        <p>本来淘汰されるべき企業が補助金で生き残っている。経営能力がない会社が生き残り、低い労働分配率の悪循環。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">宮武（地方 PE ファンドの実態）</h4>
        <p>地方は悪循環の中にいる。人口減 → 消費停滞 → 投資回収不能 → マーケット毎年 1% 縮小 → 分配率上げる余裕なし。補助金は経営者のポケットが少し増えるだけ。痛みを伴う変革は起きにくい。</p>
    </div>

    <div class="speaker-block">
        <h4 class="sb-name">黒田先生</h4>
        <p>セクター・グループによってメカニズムが全然違う。集計インデックスではなく分解して考える必要がある。アフォーダビリティの議論が日本では足りていない。</p>
    </div>

    <h4 style="color:#2c5282;margin-top:1rem;">金融政策と過剰流動性</h4>
    <ul>
        <li>2020 年コロナ以降の世界的金融緩和 → 2022 年からインフレ → アメリカは金利急上昇 → 2024 年後半からトランプ関税で再び金融緩和の動き。</li>
        <li>川口先生の仮説: <strong>過剰流動性が株価・不動産価格上昇の主因</strong>。「このお金は引かないぞ」と感じた。</li>
    </ul>

    <h4 style="color:#2c5282;margin-top:1rem;">不動産市場の動向</h4>
    <ul>
        <li>東京のマンション価格は大幅に上昇。パワーカップルでも 1.5 億〜2 億円必要。山手線内は 2 億円では買えない。</li>
        <li>家賃は瞬間風速で年率 20% 程度上昇。ワンルーム 7 万円 → 15 万円。</li>
        <li>外資（特に中国マネー）がビルを高値で買収。三菱地所社長が「ロジックが分からない」。</li>
        <li>名古屋は下落、大阪はフラット、東京だけ上昇（三極化）。</li>
    </ul>

    <h4 style="color:#2c5282;margin-top:1rem;">バブル崩壊の条件（川口先生の見解）</h4>
    <ul>
        <li>株価が上がっている間は不動産価格は下がらない（経験則・過去に例外なし）。</li>
        <li><strong>ドライパウダー（未使用投資資金）が尽きた時がバブル崩壊</strong>。実質金利マイナスなら尽きない。</li>
        <li>崩壊には日銀や金融庁による政治的決断が必要。金融庁は地銀に対して不動産融資を絞り始めたが、メガバンクにはまだ。</li>
        <li>富裕層は先に情報を得て資金を引き揚げる（リーマン・IT バブル崩壊時の米国税データで実証済み）。</li>
    </ul>

    <h4 style="color:#2c5282;margin-top:1rem;">人口減少と長期的課題</h4>
    <ul>
        <li>日本の人口減少率は毎年第二次世界大戦の死亡率と同じレベル。</li>
        <li>10〜20 年後には 47 都道府県が 5〜7 つに統合される可能性。</li>
        <li>東京は 2045 年まで大丈夫だが、それ以降は衰退する。</li>
    </ul>

    <h4 style="color:#2c5282;margin-top:1rem;">不動産セキュリティトークン (ST) の議論</h4>
    <ul>
        <li>実物不動産と J-REIT の間を埋める商品として宣伝されているが、実態は個人投資家向けの短期販売商品。</li>
        <li>法的にはグレーゾーン。J-REIT 業界は ST を排除したい。金融庁は私募 REIT より ST を推す。</li>
        <li>不動産鑑定業界をベースに、REIT・ST・実物不動産業界がいがみ合う構図。</li>
    </ul>

    <h3 style="color:#1f3a5f;margin-top:1.4rem;">6.4 次回に向けた提案（松前 景一郎）</h3>
    <ul>
        <li>不動産価格のモデリングが面白いテーマ。金利の動向をドライバーとして、マネーのネイチャー別・エリア別で分析。</li>
        <li>データが取れるなら AI を使ったプライシングモデルの構築。</li>
    </ul>

    <h3 style="color:#1f3a5f;margin-top:1.4rem;">6.5 ロジスティクス確認</h3>
    <ul>
        <li>次回は <strong>5月9日（土）10:30 開始</strong>。場所は早稲田大学。</li>
        <li>テーマ候補: 市場分析における AI の役割、ファイナンシャリゼーション（金融化）、飯沼先生の「市場分析は AI に変わってしまうか」。</li>
        <li>コミュニケーションは基本的に Facebook。</li>
        <li>終了後、神楽坂駅近くのイタリアンで食事会。</li>
    </ul>

    <div class="decision-box">
        <h3>決定事項</h3>
        <ol>
            <li><strong>次回日程</strong>: 5 月 9 日（土）10:30 開始</li>
            <li><strong>場所</strong>: 早稲田大学（教室または図書館）</li>
            <li><strong>運営方針</strong>: 1 年間の月次ディスカッション → 出版物にまとめる</li>
            <li><strong>録画・録音</strong>: 参加者の了承を得て実施（外部公開はしない）</li>
            <li><strong>コミュニケーション</strong>: Facebook グループ</li>
            <li><strong>Web 会議ツール</strong>: Google Meet</li>
        </ol>
    </div>

    <div class="action-box">
        <h3>アクションアイテム</h3>
        <ul>
            <li>☐ <strong>松前 景一郎</strong>: 早稲田大学の教室/図書館を 5 月 9 日で予約</li>
            <li>☐ <strong>川口先生</strong>: 次回のテーマ・参考ペーパーをメールで共有</li>
            <li>☐ <strong>全員</strong>: 次回テーマの候補があれば Facebook またはメールで共有</li>
        </ul>
    </div>

    <div class="note-box">
        <h3>備考</h3>
        <ul>
            <li>読売新聞社は記者会見の文字起こしに AI を使用しているが、要約等は認めていない（知的鍛錬法の一環）。</li>
            <li>株式投資で資産を 7 倍にした人が複数いる（Facebook に投稿された話）。</li>
        </ul>
    </div>

    <p style="margin-top:1.4rem;">
        <a class="nav-link" href="260411_meeting_notes.html">
            旧版（単独ページ）→
        </a>
    </p>

'''

new_text = text[:i] + new_section + text[j:]
src.write_text(new_text, encoding="utf-8")
print(f"OK: {len(text)} -> {len(new_text)} chars")
