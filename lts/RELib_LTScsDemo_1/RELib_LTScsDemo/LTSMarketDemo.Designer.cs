namespace RELib_LTScsDemo
{
    partial class LTSMarketDemo
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(LTSMarketDemo));
            this.MarketLabel = new System.Windows.Forms.Label();
            this.subcribeBtn = new System.Windows.Forms.Button();
            this.loginBtn = new System.Windows.Forms.Button();
            this.unSubcribeBtn = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // MarketLabel
            // 
            this.MarketLabel.AutoSize = true;
            this.MarketLabel.Location = new System.Drawing.Point(12, 19);
            this.MarketLabel.Name = "MarketLabel";
            this.MarketLabel.Size = new System.Drawing.Size(41, 12);
            this.MarketLabel.TabIndex = 0;
            this.MarketLabel.Text = "label1";
            // 
            // subcribeBtn
            // 
            this.subcribeBtn.Location = new System.Drawing.Point(112, 439);
            this.subcribeBtn.Name = "subcribeBtn";
            this.subcribeBtn.Size = new System.Drawing.Size(78, 52);
            this.subcribeBtn.TabIndex = 1;
            this.subcribeBtn.Text = "订阅行情";
            this.subcribeBtn.UseVisualStyleBackColor = true;
            this.subcribeBtn.Click += new System.EventHandler(this.button1_Click);
            // 
            // loginBtn
            // 
            this.loginBtn.Location = new System.Drawing.Point(12, 439);
            this.loginBtn.Name = "loginBtn";
            this.loginBtn.Size = new System.Drawing.Size(78, 52);
            this.loginBtn.TabIndex = 2;
            this.loginBtn.Text = "登录行情";
            this.loginBtn.UseVisualStyleBackColor = true;
            this.loginBtn.Click += new System.EventHandler(this.loginBtn_Click);
            // 
            // unSubcribeBtn
            // 
            this.unSubcribeBtn.Enabled = false;
            this.unSubcribeBtn.Location = new System.Drawing.Point(112, 498);
            this.unSubcribeBtn.Name = "unSubcribeBtn";
            this.unSubcribeBtn.Size = new System.Drawing.Size(78, 52);
            this.unSubcribeBtn.TabIndex = 3;
            this.unSubcribeBtn.Text = "取消订阅";
            this.unSubcribeBtn.UseVisualStyleBackColor = true;
            this.unSubcribeBtn.Click += new System.EventHandler(this.button2_Click);
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(12, 498);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(78, 52);
            this.button3.TabIndex = 4;
            this.button3.Text = "退出行情";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
            // 
            // LTSMarketDemo
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(984, 562);
            this.Controls.Add(this.button3);
            this.Controls.Add(this.unSubcribeBtn);
            this.Controls.Add(this.loginBtn);
            this.Controls.Add(this.subcribeBtn);
            this.Controls.Add(this.MarketLabel);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "LTSMarketDemo";
            this.Text = "LTS--C#版行情Demo";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label MarketLabel;
        private System.Windows.Forms.Button subcribeBtn;
        private System.Windows.Forms.Button loginBtn;
        private System.Windows.Forms.Button unSubcribeBtn;
        private System.Windows.Forms.Button button3;
    }
}

