namespace RELib_LTScsDemo
{
    partial class LTSDemo
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(LTSDemo));
            this.MarketDataGrid = new System.Windows.Forms.DataGridView();
            this.MarketDataTimer = new System.Windows.Forms.Timer(this.components);
            this.tabControlQuery = new System.Windows.Forms.TabControl();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.PositionDataGrid = new System.Windows.Forms.DataGridView();
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.TradeDataGrid = new System.Windows.Forms.DataGridView();
            this.tabPage3 = new System.Windows.Forms.TabPage();
            this.FundDataGrid = new System.Windows.Forms.DataGridView();
            this.tabPage4 = new System.Windows.Forms.TabPage();
            this.DelegateDataGrid = new System.Windows.Forms.DataGridView();
            this.panel1 = new System.Windows.Forms.Panel();
            this.textBoxPrice = new System.Windows.Forms.TextBox();
            this.radioButtonSell = new System.Windows.Forms.RadioButton();
            this.radioButtonBuy = new System.Windows.Forms.RadioButton();
            this.radioButtonClosePosi = new System.Windows.Forms.RadioButton();
            this.radioButtonOpenPosi = new System.Windows.Forms.RadioButton();
            this.button1 = new System.Windows.Forms.Button();
            this.textBoxVolume = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.textBoxName = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.comboBoxInstrument = new System.Windows.Forms.ComboBox();
            ((System.ComponentModel.ISupportInitialize)(this.MarketDataGrid)).BeginInit();
            this.tabControlQuery.SuspendLayout();
            this.tabPage1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.PositionDataGrid)).BeginInit();
            this.tabPage2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.TradeDataGrid)).BeginInit();
            this.tabPage3.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.FundDataGrid)).BeginInit();
            this.tabPage4.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.DelegateDataGrid)).BeginInit();
            this.panel1.SuspendLayout();
            this.SuspendLayout();
            // 
            // MarketDataGrid
            // 
            this.MarketDataGrid.BackgroundColor = System.Drawing.Color.White;
            this.MarketDataGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.MarketDataGrid.Dock = System.Windows.Forms.DockStyle.Top;
            this.MarketDataGrid.Location = new System.Drawing.Point(0, 0);
            this.MarketDataGrid.Name = "MarketDataGrid";
            this.MarketDataGrid.ReadOnly = true;
            this.MarketDataGrid.RowTemplate.Height = 23;
            this.MarketDataGrid.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.MarketDataGrid.Size = new System.Drawing.Size(1171, 318);
            this.MarketDataGrid.TabIndex = 0;
            this.MarketDataGrid.CellContentClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.MarketDataGrid_CellContentClick);
            // 
            // MarketDataTimer
            // 
            this.MarketDataTimer.Interval = 500;
            this.MarketDataTimer.Tick += new System.EventHandler(this.MarketDataTimer_Tick);
            // 
            // tabControlQuery
            // 
            this.tabControlQuery.Controls.Add(this.tabPage1);
            this.tabControlQuery.Controls.Add(this.tabPage2);
            this.tabControlQuery.Controls.Add(this.tabPage3);
            this.tabControlQuery.Controls.Add(this.tabPage4);
            this.tabControlQuery.Dock = System.Windows.Forms.DockStyle.Right;
            this.tabControlQuery.Location = new System.Drawing.Point(279, 318);
            this.tabControlQuery.Name = "tabControlQuery";
            this.tabControlQuery.SelectedIndex = 0;
            this.tabControlQuery.Size = new System.Drawing.Size(892, 265);
            this.tabControlQuery.TabIndex = 1;
            this.tabControlQuery.SelectedIndexChanged += new System.EventHandler(this.tabControlQuery_SelectedIndexChanged);
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.PositionDataGrid);
            this.tabPage1.Location = new System.Drawing.Point(4, 22);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage1.Size = new System.Drawing.Size(884, 239);
            this.tabPage1.TabIndex = 0;
            this.tabPage1.Text = "持仓查询";
            this.tabPage1.UseVisualStyleBackColor = true;
            // 
            // PositionDataGrid
            // 
            this.PositionDataGrid.BackgroundColor = System.Drawing.Color.White;
            this.PositionDataGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.PositionDataGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.PositionDataGrid.Location = new System.Drawing.Point(3, 3);
            this.PositionDataGrid.Name = "PositionDataGrid";
            this.PositionDataGrid.RowTemplate.Height = 23;
            this.PositionDataGrid.Size = new System.Drawing.Size(878, 233);
            this.PositionDataGrid.TabIndex = 0;
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.TradeDataGrid);
            this.tabPage2.Location = new System.Drawing.Point(4, 22);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage2.Size = new System.Drawing.Size(884, 239);
            this.tabPage2.TabIndex = 1;
            this.tabPage2.Text = "成交回报";
            this.tabPage2.UseVisualStyleBackColor = true;
            // 
            // TradeDataGrid
            // 
            this.TradeDataGrid.BackgroundColor = System.Drawing.Color.White;
            this.TradeDataGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.TradeDataGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.TradeDataGrid.Location = new System.Drawing.Point(3, 3);
            this.TradeDataGrid.Name = "TradeDataGrid";
            this.TradeDataGrid.RowTemplate.Height = 23;
            this.TradeDataGrid.Size = new System.Drawing.Size(878, 233);
            this.TradeDataGrid.TabIndex = 1;
            // 
            // tabPage3
            // 
            this.tabPage3.Controls.Add(this.FundDataGrid);
            this.tabPage3.Location = new System.Drawing.Point(4, 22);
            this.tabPage3.Name = "tabPage3";
            this.tabPage3.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage3.Size = new System.Drawing.Size(884, 239);
            this.tabPage3.TabIndex = 2;
            this.tabPage3.Text = "资金查询";
            this.tabPage3.UseVisualStyleBackColor = true;
            // 
            // FundDataGrid
            // 
            this.FundDataGrid.BackgroundColor = System.Drawing.Color.White;
            this.FundDataGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.FundDataGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.FundDataGrid.Location = new System.Drawing.Point(3, 3);
            this.FundDataGrid.Name = "FundDataGrid";
            this.FundDataGrid.RowTemplate.Height = 23;
            this.FundDataGrid.Size = new System.Drawing.Size(878, 233);
            this.FundDataGrid.TabIndex = 1;
            // 
            // tabPage4
            // 
            this.tabPage4.Controls.Add(this.DelegateDataGrid);
            this.tabPage4.Location = new System.Drawing.Point(4, 22);
            this.tabPage4.Name = "tabPage4";
            this.tabPage4.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage4.Size = new System.Drawing.Size(884, 239);
            this.tabPage4.TabIndex = 3;
            this.tabPage4.Text = "委托回报";
            this.tabPage4.UseVisualStyleBackColor = true;
            // 
            // DelegateDataGrid
            // 
            this.DelegateDataGrid.BackgroundColor = System.Drawing.Color.White;
            this.DelegateDataGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.DelegateDataGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.DelegateDataGrid.Location = new System.Drawing.Point(3, 3);
            this.DelegateDataGrid.Name = "DelegateDataGrid";
            this.DelegateDataGrid.RowTemplate.Height = 23;
            this.DelegateDataGrid.Size = new System.Drawing.Size(878, 233);
            this.DelegateDataGrid.TabIndex = 1;
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.textBoxPrice);
            this.panel1.Controls.Add(this.radioButtonSell);
            this.panel1.Controls.Add(this.radioButtonBuy);
            this.panel1.Controls.Add(this.radioButtonClosePosi);
            this.panel1.Controls.Add(this.radioButtonOpenPosi);
            this.panel1.Controls.Add(this.button1);
            this.panel1.Controls.Add(this.textBoxVolume);
            this.panel1.Controls.Add(this.label6);
            this.panel1.Controls.Add(this.label5);
            this.panel1.Controls.Add(this.label4);
            this.panel1.Controls.Add(this.label3);
            this.panel1.Controls.Add(this.textBoxName);
            this.panel1.Controls.Add(this.label2);
            this.panel1.Controls.Add(this.label1);
            this.panel1.Controls.Add(this.comboBoxInstrument);
            this.panel1.Dock = System.Windows.Forms.DockStyle.Left;
            this.panel1.Location = new System.Drawing.Point(0, 318);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(283, 265);
            this.panel1.TabIndex = 2;
            // 
            // textBoxPrice
            // 
            this.textBoxPrice.Location = new System.Drawing.Point(35, 119);
            this.textBoxPrice.Name = "textBoxPrice";
            this.textBoxPrice.Size = new System.Drawing.Size(121, 21);
            this.textBoxPrice.TabIndex = 8;
            // 
            // radioButtonSell
            // 
            this.radioButtonSell.AutoSize = true;
            this.radioButtonSell.Location = new System.Drawing.Point(117, 86);
            this.radioButtonSell.Name = "radioButtonSell";
            this.radioButtonSell.Size = new System.Drawing.Size(35, 16);
            this.radioButtonSell.TabIndex = 14;
            this.radioButtonSell.Text = "卖";
            this.radioButtonSell.UseVisualStyleBackColor = true;
            // 
            // radioButtonBuy
            // 
            this.radioButtonBuy.AutoSize = true;
            this.radioButtonBuy.Checked = true;
            this.radioButtonBuy.Location = new System.Drawing.Point(39, 86);
            this.radioButtonBuy.Name = "radioButtonBuy";
            this.radioButtonBuy.Size = new System.Drawing.Size(35, 16);
            this.radioButtonBuy.TabIndex = 13;
            this.radioButtonBuy.TabStop = true;
            this.radioButtonBuy.Text = "买";
            this.radioButtonBuy.UseVisualStyleBackColor = true;
            // 
            // radioButtonClosePosi
            // 
            this.radioButtonClosePosi.AutoSize = true;
            this.radioButtonClosePosi.Location = new System.Drawing.Point(117, 123);
            this.radioButtonClosePosi.Name = "radioButtonClosePosi";
            this.radioButtonClosePosi.Size = new System.Drawing.Size(35, 16);
            this.radioButtonClosePosi.TabIndex = 12;
            this.radioButtonClosePosi.Text = "平";
            this.radioButtonClosePosi.UseVisualStyleBackColor = true;
            this.radioButtonClosePosi.Visible = false;
            // 
            // radioButtonOpenPosi
            // 
            this.radioButtonOpenPosi.AutoSize = true;
            this.radioButtonOpenPosi.Location = new System.Drawing.Point(39, 123);
            this.radioButtonOpenPosi.Name = "radioButtonOpenPosi";
            this.radioButtonOpenPosi.Size = new System.Drawing.Size(35, 16);
            this.radioButtonOpenPosi.TabIndex = 11;
            this.radioButtonOpenPosi.Text = "开";
            this.radioButtonOpenPosi.UseVisualStyleBackColor = true;
            this.radioButtonOpenPosi.Visible = false;
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(5, 200);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(164, 41);
            this.button1.TabIndex = 10;
            this.button1.Text = "下单";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // textBoxVolume
            // 
            this.textBoxVolume.Location = new System.Drawing.Point(35, 156);
            this.textBoxVolume.Name = "textBoxVolume";
            this.textBoxVolume.Size = new System.Drawing.Size(121, 21);
            this.textBoxVolume.TabIndex = 9;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(0, 161);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(29, 12);
            this.label6.TabIndex = 7;
            this.label6.Text = "数量";
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(0, 127);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(29, 12);
            this.label5.TabIndex = 6;
            this.label5.Text = "价格";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(0, 123);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(29, 12);
            this.label4.TabIndex = 5;
            this.label4.Text = "开平";
            this.label4.Visible = false;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(3, 86);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(29, 12);
            this.label3.TabIndex = 4;
            this.label3.Text = "买卖";
            // 
            // textBoxName
            // 
            this.textBoxName.Location = new System.Drawing.Point(35, 43);
            this.textBoxName.Name = "textBoxName";
            this.textBoxName.Size = new System.Drawing.Size(121, 21);
            this.textBoxName.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(3, 47);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(29, 12);
            this.label2.TabIndex = 2;
            this.label2.Text = "名称";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(2, 14);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(29, 12);
            this.label1.TabIndex = 1;
            this.label1.Text = "合约";
            // 
            // comboBoxInstrument
            // 
            this.comboBoxInstrument.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxInstrument.FormattingEnabled = true;
            this.comboBoxInstrument.Location = new System.Drawing.Point(35, 11);
            this.comboBoxInstrument.Name = "comboBoxInstrument";
            this.comboBoxInstrument.Size = new System.Drawing.Size(223, 20);
            this.comboBoxInstrument.TabIndex = 0;
            this.comboBoxInstrument.SelectedIndexChanged += new System.EventHandler(this.comboBoxInstrument_SelectedIndexChanged);
            // 
            // LTSDemo
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1171, 583);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.tabControlQuery);
            this.Controls.Add(this.MarketDataGrid);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "LTSDemo";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "LTSCSharpDemo";
            ((System.ComponentModel.ISupportInitialize)(this.MarketDataGrid)).EndInit();
            this.tabControlQuery.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.PositionDataGrid)).EndInit();
            this.tabPage2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.TradeDataGrid)).EndInit();
            this.tabPage3.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.FundDataGrid)).EndInit();
            this.tabPage4.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.DelegateDataGrid)).EndInit();
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.DataGridView MarketDataGrid;
        private System.Windows.Forms.Timer MarketDataTimer;
        private System.Windows.Forms.TabControl tabControlQuery;
        private System.Windows.Forms.TabPage tabPage1;
        private System.Windows.Forms.TabPage tabPage2;
        private System.Windows.Forms.DataGridView PositionDataGrid;
        private System.Windows.Forms.TabPage tabPage3;
        private System.Windows.Forms.TabPage tabPage4;
        private System.Windows.Forms.DataGridView TradeDataGrid;
        private System.Windows.Forms.DataGridView DelegateDataGrid;
        private System.Windows.Forms.DataGridView FundDataGrid;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox comboBoxInstrument;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox textBoxName;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.TextBox textBoxVolume;
        private System.Windows.Forms.TextBox textBoxPrice;
        private System.Windows.Forms.RadioButton radioButtonOpenPosi;
        private System.Windows.Forms.RadioButton radioButtonClosePosi;
        private System.Windows.Forms.RadioButton radioButtonBuy;
        private System.Windows.Forms.RadioButton radioButtonSell;
    }
}